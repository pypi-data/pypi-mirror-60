# Copyright(c) 2019 Jake Fowler
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use, 
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, 
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

import clr
from System import DateTime, Func, Double, Array
from System.Collections.Generic import List
from pathlib import Path
clr.AddReference(str(Path("cmdty_storage/lib/Cmdty.TimePeriodValueTypes")))
from Cmdty.TimePeriodValueTypes import QuarterHour, HalfHour, Hour, Day, Month, Quarter, TimePeriodFactory

clr.AddReference(str(Path('cmdty_storage/lib/Cmdty.Storage')))
from Cmdty.Storage import IBuilder, IAddInjectWithdrawConstraints, InjectWithdrawRangeByInventoryAndPeriod, InjectWithdrawRangeByInventory, \
    CmdtyStorageBuilderExtensions, IAddInjectionCost, IAddCmdtyConsumedOnInject, IAddWithdrawalCost, IAddCmdtyConsumedOnWithdraw, \
    IAddMinInventory, IAddMaxInventory, \
    IAddCmdtyInventoryLoss, IAddCmdtyInventoryCost, IAddTerminalStorageState, IBuildCmdtyStorage
from Cmdty.Storage import CmdtyStorage as NetCmdtyStorage
from Cmdty.Storage import InjectWithdrawRange as NetInjectWithdrawRange

from Cmdty.Storage import IntrinsicStorageValuation, IIntrinsicAddStartingInventory, IIntrinsicAddCurrentPeriod, IIntrinsicAddForwardCurve, \
    IIntrinsicAddCmdtySettlementRule, IIntrinsicAddDiscountFactorFunc, \
    IIntrinsicAddNumericalTolerance, IIntrinsicCalculate, IntrinsicStorageValuationExtensions

clr.AddReference(str(Path('cmdty_storage/lib/Cmdty.TimeSeries')))
from Cmdty.TimeSeries import TimeSeries

from collections import namedtuple
from datetime import datetime
import pandas as pd

IntrinsicValuationResults = namedtuple('IntrinsicValuationResults', 'npv, profile')
InjectWithdrawByInventory = namedtuple('InjectWithdrawByInventory', 'inventory, min_rate, max_rate')
InjectWithdrawByInventoryAndPeriod = namedtuple('InjectWithdrawByInventoryPeriod', 'period, rates_by_inventory')
InjectWithdrawRange = namedtuple('InjectWithdrawRange', 'min_inject_withdraw_rate, max_inject_withdraw_rate')

def _from_datetime_like(datetime_like, time_period_type):
    """ Converts either a pandas Period, datetime or date to a .NET Time Period"""

    if (hasattr(datetime_like, 'hour')):
        time_args = (datetime_like.hour, datetime_like.minute, datetime_like.second)
    else:
        time_args = (0, 0, 0)

    date_time = DateTime(datetime_like.year, datetime_like.month, datetime_like.day, *time_args)
    return TimePeriodFactory.FromDateTime[time_period_type](date_time)


def _net_datetime_to_py_datetime(net_datetime):
    return datetime(net_datetime.Year, net_datetime.Month, net_datetime.Day, net_datetime.Hour, net_datetime.Minute, net_datetime.Second, net_datetime.Millisecond * 1000)


def _net_time_period_to_pandas_period(net_time_period, freq):
    start_datetime = _net_datetime_to_py_datetime(net_time_period.Start)
    return pd.Period(start_datetime, freq=freq)


def _series_to_double_time_series(series, time_period_type):
    """Converts an instance of pandas Series to a Cmdty.TimeSeries.TimeSeries type with Double data type."""
    return _series_to_time_series(series, time_period_type, Double, lambda x: x)


def _series_to_time_series(series, time_period_type, net_data_type, data_selector):
    """Converts an instance of pandas Series to a Cmdty.TimeSeries.TimeSeries."""
    series_len = len(series)
    net_indices = Array.CreateInstance(time_period_type, series_len)
    net_values = Array.CreateInstance(net_data_type, series_len)

    for i in range(series_len):
        net_indices[i] = _from_datetime_like(series.index[i], time_period_type)
        net_values[i] = data_selector(series.values[i])

    return TimeSeries[time_period_type, net_data_type](net_indices, net_values)


def _net_time_series_to_pandas_series(net_time_series, freq):
    """Converts an instance of class Cmdty.TimeSeries.TimeSeries to a pandas Series"""

    curve_start = net_time_series.Indices[0].Start

    curve_start_datetime = _net_datetime_to_py_datetime(curve_start)
    
    index = pd.period_range(start=curve_start_datetime, freq=freq, periods=net_time_series.Count)
    
    prices = [net_time_series.Data[idx] for idx in range(0, net_time_series.Count)]

    return pd.Series(prices, index)


def _is_scalar(arg):
    return isinstance(arg, int) or isinstance(arg, float)


def _raise_if_none(arg, error_message):
    if arg is None:
        raise ValueError(error_message)


def _raise_if_not_none(arg, error_message):
    if arg is not None:
        raise ValueError(error_message)


FREQ_TO_PERIOD_TYPE = {
        "15min" : QuarterHour,
        "30min" : HalfHour,
        "H" : Hour,
        "D" : Day,
        "M" : Month,
        "Q" : Quarter
    }
""" dict of str: .NET time period type.
Each item describes an allowable granularity of curves constructed, as specified by the 
freq parameter in the curves public methods.

The keys represent the pandas Offset Alias which describe the granularity, and will generally be used
    as the freq of the pandas Series objects returned by the curve construction methods.
The values are the associated .NET time period types used in behind-the-scenes calculations.
"""


def intrinsic_value(cmdty_storage, val_date, inventory, forward_curve, settlement_rule, interest_rates, 
                    num_inventory_grid_points=100, numerical_tolerance=1E-12):
    """
    Calculates the intrinsic value of cmdty storage.

    Args:
        settlement_rule (callable): Mapping function from pandas.Period type to the date on which the cmdty delivered in
            this period is settled. The pandas.Period parameter will have freq equal to the cmdty_storage parameter's freq property.
    """

    if cmdty_storage.freq != forward_curve.index.freqstr:
        raise ValueError("cmdty_storage and forward_curve have different frequencies.")

    time_period_type = FREQ_TO_PERIOD_TYPE[cmdty_storage.freq]
    intrinsic_calc = IntrinsicStorageValuation[time_period_type].ForStorage(cmdty_storage.net_storage)

    IIntrinsicAddStartingInventory[time_period_type](intrinsic_calc).WithStartingInventory(inventory)

    current_period = _from_datetime_like(val_date, time_period_type)
    IIntrinsicAddCurrentPeriod[time_period_type](intrinsic_calc).ForCurrentPeriod(current_period)

    net_forward_curve = _series_to_double_time_series(forward_curve, time_period_type)
    IIntrinsicAddForwardCurve[time_period_type](intrinsic_calc).WithForwardCurve(net_forward_curve)

    def wrapper_settle_function(py_function, net_time_period, freq):
        pandas_period = _net_time_period_to_pandas_period(net_time_period, freq)
        py_function_result = py_function(pandas_period)
        net_settle_day = _from_datetime_like(py_function_result, Day)
        return net_settle_day

    def wrapped_function(net_time_period):
        return wrapper_settle_function(settlement_rule, net_time_period, cmdty_storage.freq)

    net_settlement_rule = Func[time_period_type, Day](wrapped_function)
    IIntrinsicAddCmdtySettlementRule[time_period_type](intrinsic_calc).WithCmdtySettlementRule(net_settlement_rule)
    
    interest_rate_time_series = _series_to_double_time_series(interest_rates, FREQ_TO_PERIOD_TYPE['D'])
    IntrinsicStorageValuationExtensions.WithAct365ContinuouslyCompoundedInterestRateCurve[time_period_type](intrinsic_calc, interest_rate_time_series)

    IntrinsicStorageValuationExtensions.WithFixedNumberOfPointsOnGlobalInventoryRange[time_period_type](intrinsic_calc, num_inventory_grid_points)

    IntrinsicStorageValuationExtensions.WithLinearInventorySpaceInterpolation[time_period_type](intrinsic_calc)

    IIntrinsicAddNumericalTolerance[time_period_type](intrinsic_calc).WithNumericalTolerance(numerical_tolerance)

    net_val_results = IIntrinsicCalculate[time_period_type](intrinsic_calc).Calculate()

    net_profile = net_val_results.StorageProfile
    if net_profile.Count == 0:
        index = pd.PeriodIndex(data=[], freq=cmdty_storage.freq)
    else:
        profile_start = _net_datetime_to_py_datetime(net_profile.Indices[0].Start)
        index = pd.period_range(start=profile_start, freq=cmdty_storage.freq, periods=net_profile.Count)

    inventories = [None] * net_profile.Count
    inject_withdraw_volumes = [None] * net_profile.Count
    cmdty_consumed = [None] * net_profile.Count
    inventory_loss = [None] * net_profile.Count
    net_position = [None] * net_profile.Count

    for i, profile_data in enumerate(net_profile.Data):
        inventories[i] = profile_data.Inventory
        inject_withdraw_volumes[i] = profile_data.InjectWithdrawVolume
        cmdty_consumed[i] = profile_data.CmdtyConsumed
        inventory_loss[i] = profile_data.InventoryLoss
        net_position[i] = profile_data.NetPosition

    data_frame_data = {'inventory' : inventories, 'inject_withdraw_volume' : inject_withdraw_volumes,
                  'cmdty_consumed' : cmdty_consumed, 'inventory_loss' : inventory_loss, 'net_position' : net_position}
    data_frame = pd.DataFrame(data=data_frame_data, index=index)
    
    return IntrinsicValuationResults(net_val_results.NetPresentValue, data_frame)


class CmdtyStorage:

    def __init__(self, freq, storage_start, storage_end, 
                   injection_cost, withdrawal_cost, 
                   constraints=None,
                   min_inventory=None, max_inventory=None, max_injection_rate=None, max_withdrawal_rate=None,
                   cmdty_consumed_inject=None, cmdty_consumed_withdraw=None,
                   terminal_storage_npv=None,
                   inventory_loss=None, inventory_cost=None):
                 
        if freq not in FREQ_TO_PERIOD_TYPE:
            raise ValueError("freq parameter value of '{}' not supported. The allowable values can be found in the keys of the dict curves.FREQ_TO_PERIOD_TYPE.".format(freq))

        time_period_type = FREQ_TO_PERIOD_TYPE[freq]

        start_period = _from_datetime_like(storage_start, time_period_type)
        end_period = _from_datetime_like(storage_end, time_period_type)

        builder = IBuilder[time_period_type](NetCmdtyStorage[time_period_type].Builder)
    
        builder = builder.WithActiveTimePeriod(start_period, end_period)

        net_constraints = List[InjectWithdrawRangeByInventoryAndPeriod[time_period_type]]()

        if constraints is not None:
            _raise_if_not_none(min_inventory, "min_inventory parameter should not be provided if constraints parameter is provided.")
            _raise_if_not_none(max_inventory, "max_inventory parameter should not be provided if constraints parameter is provided.")
            _raise_if_not_none(max_injection_rate, "max_injection_rate parameter should not be provided if constraints parameter is provided.")
            _raise_if_not_none(max_withdrawal_rate, "max_withdrawal_rate parameter should not be provided if constraints parameter is provided.")
            
            for period, rates_by_inventory in constraints:
                net_period = _from_datetime_like(period, time_period_type)
                net_rates_by_inventory = List[InjectWithdrawRangeByInventory]()
                for inventory, min_rate, max_rate in rates_by_inventory:
                    net_rates_by_inventory.Add(InjectWithdrawRangeByInventory(inventory, NetInjectWithdrawRange(min_rate, max_rate)))
                net_constraints.Add(InjectWithdrawRangeByInventoryAndPeriod[time_period_type](net_period, net_rates_by_inventory))

            builder = IAddInjectWithdrawConstraints[time_period_type](builder)
            CmdtyStorageBuilderExtensions.WithTimeAndInventoryVaryingInjectWithdrawRatesPiecewiseLinear[time_period_type](builder, net_constraints)

        else:
            _raise_if_none(min_inventory, "min_inventory parameter should be provided if constraints parameter is not provided.")
            _raise_if_none(max_inventory, "max_inventory parameter should be provided if constraints parameter is not provided.")
            _raise_if_none(max_injection_rate, "max_injection_rate parameter should be provided if constraints parameter is not provided.")
            _raise_if_none(max_withdrawal_rate, "max_withdrawal_rate parameter should be provided if constraints parameter is not provided.")
            
            builder = IAddInjectWithdrawConstraints[time_period_type](builder)
            
            max_injection_rate_is_scalar = _is_scalar(max_injection_rate)
            max_withdrawal_rate_is_scalar = _is_scalar(max_withdrawal_rate)
            
            if max_injection_rate_is_scalar and max_withdrawal_rate_is_scalar:
                CmdtyStorageBuilderExtensions.WithConstantInjectWithdrawRange[time_period_type](builder, -max_withdrawal_rate, max_injection_rate)
            else:
                if max_injection_rate_is_scalar:
                    max_injection_rate = pd.Series(data=[max_injection_rate] * len(max_withdrawal_rate), index=max_withdrawal_rate.index)
                elif max_withdrawal_rate_is_scalar:
                    max_withdrawal_rate = pd.Series(data=[max_withdrawal_rate] * len(max_injection_rate), index=max_injection_rate.index)

                inject_withdraw_series = max_injection_rate.combine(max_withdrawal_rate, lambda inj_rate, with_rate: (-with_rate, inj_rate)).dropna()
                net_inj_with_series = _series_to_time_series(inject_withdraw_series, time_period_type, NetInjectWithdrawRange, lambda tup: NetInjectWithdrawRange(tup[0], tup[1]))
                builder.WithInjectWithdrawRangeSeries(net_inj_with_series)

            builder = IAddMinInventory[time_period_type](builder)
            if isinstance(min_inventory, pd.Series):
                net_series_min_inventory = _series_to_double_time_series(min_inventory, time_period_type)
                builder.WithMinInventoryTimeSeries(net_series_min_inventory)
            else: # Assume min_inventory is a constaint number
                builder.WithConstantMinInventory(min_inventory)

            builder = IAddMaxInventory[time_period_type](builder)
            if isinstance(max_inventory, pd.Series):
                net_series_max_inventory = _series_to_double_time_series(max_inventory, time_period_type)
                builder.WithMaxInventoryTimeSeries(net_series_max_inventory)
            else: # Assume max_inventory is a constaint number
                builder.WithConstantMaxInventory(max_inventory)

        builder = IAddInjectionCost[time_period_type](builder)

        if _is_scalar(injection_cost):
            builder.WithPerUnitInjectionCost(injection_cost)
        else:
            net_series_injection_cost = _series_to_double_time_series(injection_cost, time_period_type)
            builder.WithPerUnitInjectionCostTimeSeries(net_series_injection_cost)
    
        builder = IAddCmdtyConsumedOnInject[time_period_type](builder)

        if cmdty_consumed_inject is not None:
            if _is_scalar(cmdty_consumed_inject):
                builder.WithFixedPercentCmdtyConsumedOnInject(cmdty_consumed_inject)
            else:
                net_series_cmdty_consumed_inject = _series_to_double_time_series(cmdty_consumed_inject, time_period_type)
                builder.WithPercentCmdtyConsumedOnInjectTimeSeries(net_series_cmdty_consumed_inject)
        else:
            builder.WithNoCmdtyConsumedOnInject()
        
        builder = IAddWithdrawalCost[time_period_type](builder)
        if _is_scalar(withdrawal_cost):
            builder.WithPerUnitWithdrawalCost(withdrawal_cost)
        else:
            net_series_withdrawal_cost = _series_to_double_time_series(withdrawal_cost, time_period_type)
            builder.WithPerUnitWithdrawalCostTimeSeries(net_series_withdrawal_cost)

        builder = IAddCmdtyConsumedOnWithdraw[time_period_type](builder)

        if cmdty_consumed_withdraw is not None:
            if _is_scalar(cmdty_consumed_withdraw):
                builder.WithFixedPercentCmdtyConsumedOnWithdraw(cmdty_consumed_withdraw)
            else:
                net_series_cmdty_consumed_withdraw = _series_to_double_time_series(cmdty_consumed_withdraw, time_period_type)
                builder.WithPercentCmdtyConsumedOnWithdrawTimeSeries(net_series_cmdty_consumed_withdraw)
        else:
            builder.WithNoCmdtyConsumedOnWithdraw()
        
        builder = IAddCmdtyInventoryLoss[time_period_type](builder)
        if inventory_loss is not None:
            if _is_scalar(inventory_loss):
                builder.WithFixedPercentCmdtyInventoryLoss(inventory_loss)
            else:
                net_series_inventory_loss = _series_to_double_time_series(inventory_loss, time_period_type)
                builder.WithCmdtyInventoryLossTimeSeries(net_series_inventory_loss)
        else:
            builder.WithNoCmdtyInventoryLoss()

        builder = IAddCmdtyInventoryCost[time_period_type](builder)
        if inventory_cost is not None:
            if _is_scalar(inventory_cost):
                builder.WithFixedPerUnitInventoryCost(inventory_cost)
            else:
                net_series_inventory_cost = _series_to_double_time_series(inventory_cost, time_period_type)
                builder.WithPerUnitInventoryCostTimeSeries(net_series_inventory_cost)
        else:
            builder.WithNoInventoryCost()

        builder = IAddTerminalStorageState[time_period_type](builder)
        
        if terminal_storage_npv is None:
            builder.MustBeEmptyAtEnd()
        else:
            builder.WithTerminalInventoryNpv(Func[Double, Double, Double](terminal_storage_npv))

        self._net_storage = IBuildCmdtyStorage[time_period_type](builder).Build()
        self._freq = freq

    def _net_time_period(self, period):
        time_period_type = FREQ_TO_PERIOD_TYPE[self._freq]
        return _from_datetime_like(period, time_period_type)
    
    @property
    def net_storage(self):
        return self._net_storage

    @property
    def freq(self):
        return self._freq

    @property
    def empty_at_end(self):
        return self._net_storage.MustBeEmptyAtEnd
    
    @property
    def start(self):
        return _net_time_period_to_pandas_period(self._net_storage.StartPeriod, self._freq)

    @property
    def end(self):
        return _net_time_period_to_pandas_period(self._net_storage.EndPeriod, self._freq)

    def inject_withdraw_range(self, period, inventory):

        net_time_period = self._net_time_period(period)
        net_inject_withdraw = self._net_storage.GetInjectWithdrawRange(net_time_period, inventory)
        
        return InjectWithdrawRange(net_inject_withdraw.MinInjectWithdrawRate, net_inject_withdraw.MaxInjectWithdrawRate)

    def min_inventory(self, period):
        net_time_period = self._net_time_period(period)
        return self._net_storage.MinInventory(net_time_period)

    def max_inventory(self, period):
        net_time_period = self._net_time_period(period)
        return self._net_storage.MaxInventory(net_time_period)

    def injection_cost(self, period, inventory, injected_volume):
        net_time_period = self._net_time_period(period)
        net_inject_costs = self._net_storage.InjectionCost(net_time_period, inventory, injected_volume)
        if net_inject_costs.Length > 0:
            return net_inject_costs[0].Amount
        return 0.0

    def cmdty_consumed_inject(self, period, inventory, injected_volume):
        net_time_period = self._net_time_period(period)
        return self._net_storage.CmdtyVolumeConsumedOnInject(net_time_period, inventory, injected_volume)
    
    def withdrawal_cost(self, period, inventory, withdrawn_volume):
        net_time_period = self._net_time_period(period)
        net_withdrawal_costs = self._net_storage.WithdrawalCost(net_time_period, inventory, withdrawn_volume)
        if net_withdrawal_costs.Length > 0:
            return net_withdrawal_costs[0].Amount
        return 0.0

    def cmdty_consumed_withdraw(self, period, inventory, withdrawn_volume):
        net_time_period = self._net_time_period(period)
        return self._net_storage.CmdtyVolumeConsumedOnWithdraw(net_time_period, inventory, withdrawn_volume)

    def terminal_storage_npv(self, cmdty_price, terminal_inventory):
        return self._net_storage.TerminalStorageNpv(cmdty_price, terminal_inventory)

    def inventory_pcnt_loss(self, period):
        net_time_period = self._net_time_period(period)
        return self._net_storage.CmdtyInventoryPercentLoss(net_time_period)

    def inventory_cost(self, period, inventory):
        net_time_period = self._net_time_period(period)
        net_inventory_cost = self._net_storage.CmdtyInventoryCost(net_time_period, inventory)
        if len(net_inventory_cost) > 0:
            return net_inventory_cost[0].Amount
        return 0.0


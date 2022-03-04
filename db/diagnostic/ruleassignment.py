import operator
import numpy as np

class RuleAssignment():
    """
    Menghitung mnemonic beserta fungsi-fungsi private yang diperlukan
    ...

    Attributes
    ----------
    tag : TagBuilder
        Objek TagBuilder berisi nilai atribut Runtime dan ModelTag yang
        diperlukan

    Methods
    -------
    method(x):
        descriptions
    """
    comp_operator = {
        '=': operator.eq,
        '>': operator.gt,
        '<': operator.lt,
        '>=': operator.ge,
        '<=': operator.le,
        '!=': operator.ne
    }

    def __init__(self, tag):
        self.tag = tag

    #private
    def window_ratio(self, true_size, values, comparison, threshold, required_size):
        # check required good size
        if np.count_nonzero(~np.isnan(values)) < required_size: return False

        # check if nan available in data
        if np.isnan(values).any():  # there is/are nan/s
            # calculate ratio true size
            ratio_true_size = true_size / len(values)

            # filter non nan
            non_nan = [val for val in values if ~np.isnan(val)]

            # compare values with threshold
            comp = [True if self.comp_operator.get(comparison)(v,threshold) else False for v in non_nan]
            ratio_non_nan = np.sum(comp) / len(comp)

            return True if ratio_non_nan >= ratio_true_size else False
        else: # there is not nan
            # compare values with threshold
            comp = [True if self.comp_operator.get(comparison)(v,threshold) else False for v in values]
            return True if np.sum(comp) >= true_size else False

    #private
    def moving_average(self, a, n=2) :
        ret = np.cumsum(a, dtype=float)
        ret[n:] = ret[n:] - ret[:-n]
        return ret[n - 1:] / n

    #private
    def smoothing(self, values, fn="olympic"):
        if fn == "olympic":
            # delete min and max value
            values = np.delete(values, values.argmin())
            values = np.delete(values, values.argmax())
            # values.remove(max(values))
            # values.remove(min(values))
            # moving average with window = 2
            values = self.moving_average(values, n=2)
            return values

    #private
    def is_step(self, values, step_up_threshold, step_down_threshold):
        # check values
        # if len(values) < 4: return "You need at least 4 observations!"
        if len(values) < 4: return False

        # exclude the most recent values
        history = values[:-1]
        history = self.smoothing(history)
        avg_value = np.mean(history)

        # get the two most recent observation
        obs = values[-2:]

        # check NaN
        if step_up_threshold == "NaN":
            rule_val1 = obs[0] - avg_value < -abs(step_down_threshold)
            rule_val2 = obs[1] - avg_value < -abs(step_down_threshold)
        elif step_down_threshold == "NaN":
            rule_val1 = obs[0] - avg_value > abs(step_up_threshold)
            rule_val2 = obs[1] - avg_value > abs(step_up_threshold)
        else:
            rule_val1 = (obs[0] - avg_value > abs(step_up_threshold)) or (obs[0] - avg_value < -abs(step_down_threshold))
            rule_val2 = (obs[1] - avg_value > abs(step_up_threshold)) or (obs[1] - avg_value < -abs(step_down_threshold))

        return rule_val1 and rule_val2

    def high(self, tag) -> bool:
        rule1 = self.window_ratio(16, tag.ResidualIndicationPositive(18), "=", 1, 9)
        rule2 = np.squeeze(tag.Residual(1)) >= tag.ResidualPositiveThreshold()
        return rule1 and rule2

    def very_high(self, tag) -> bool:
        rule1 = self.window_ratio(8, tag.ResidualIndicationPositive(9), "=", 1, 6)
        rule2 = self.window_ratio(6, tag.Residual(9), ">=", (2.*tag.ResidualPositiveThreshold()),6)
        rule3 = np.squeeze(tag.Residual(1)) >= (2.*tag.ResidualPositiveThreshold())
        return rule1 and rule2 and rule3

    def step_high(self, tag) -> bool:
        rule1 = self.is_step(values=tag.Actual(7),
                        step_up_threshold=2.5*tag.ResidualPositiveThreshold(),
                        step_down_threshold="NaN")
        rule2 = np.squeeze(tag.Residual(1)) > 1.5*tag.ResidualPositiveThreshold()
        return rule1 and rule2

    def step_very_high(self, tag) -> bool:
        rule1 = self.is_step(values=tag.Actual(7),
                        step_up_threshold=3.*tag.ResidualPositiveThreshold(),
                        step_down_threshold="NaN")
        rule2 = np.squeeze(tag.Residual(1)) > 2.*tag.ResidualPositiveThreshold()
        rule3 = np.squeeze(tag.ResidualIndicationPositive(1)) == 1
        return rule1 and rule2 and rule3

    #private
    def math_variance(self, values, lower_threshold="NaN", upper_threshold="NaN"):
        # variance with threshold not implemented yet
        return np.var(values)

    #private
    def math_minimum(self, values, lower_threshold="NaN", upper_threshold="NaN"):
        # minimum with threshold not implemented yet
        return np.min(values)

    def variance(self, tag) -> bool:
        rule1 = self.math_variance(tag.Residual(18)) > (4*self.math_minimum([abs(tag.ResidualPositiveThreshold()), abs(tag.ResidualPositiveThreshold())])**2)
        rule2 = self.window_ratio(true_size=2,
                             values=tag.Residual(6),
                             comparison=">=",
                             threshold=self.math_minimum([abs(tag.ResidualPositiveThreshold()), abs(tag.ResidualPositiveThreshold())]),
                             required_size=4)
        rule3 = self.window_ratio(true_size=2,
                             values=tag.Residual(6),
                             comparison="<=",
                             threshold=-1*self.math_minimum([abs(tag.ResidualPositiveThreshold()), abs(tag.ResidualPositiveThreshold())]),
                             required_size=4)
        return rule1 and rule2 and rule3

    def actual_high_model(self, tag) -> bool:
        rule1 = self.window_ratio(5, tag.Actual(6), ">=", tag.ActualHigh(), 4)
        rule2 = tag.ActiveInModel()
        rule3 = np.squeeze(tag.Actual(1)) >= tag.ActualHigh()
        return rule1 and rule2 and rule3

    def low(self, tag) -> bool:
        rule1 = self.window_ratio(16, tag.ResidualIndicationNegative(18), "=", 1, 9)
        rule2 = np.squeeze(tag.Residual()) <= tag.ResidualNegativeThreshold()
        return rule1 and rule2

    def long_high(self, tag) -> bool:
        rule1 = self.window_ratio(45, tag.ResidualIndicationPositive(48), "=", 1, 24)
        rule2 = np.squeeze(tag.Residual(1)) <= tag.ResidualPositiveThreshold()
        return rule1 and rule2

    def step_low(self, tag) -> bool:
        rule1 = self.is_step(tag.Actual(7), "NaN", 2.5*tag.ResidualNegativeThreshold())
        rule2 = np.squeeze(tag.Residual(1)) < (1.5*tag.ResidualNegativeThreshold())
        return rule1 and rule2
    
    def step_very_low(self, tag) -> bool:
        rule1 = self.is_step(tag.Actual(7), "NaN", 3.*tag.ResidualNegativeThreshold())
        rule2 = np.squeeze(tag.Residual(1)) < (2.*tag.ResidualNegativeThreshold())
        rule3 = np.squeeze(tag.ResidualIndicationNegative()) == 1
        return rule1 and rule2 and rule3

    def very_low(self, tag) -> bool:
        rule1 = self.window_ratio(8, tag.ResidualIndicationNegative(9), "=", 1, 6)
        rule2 = self.window_ratio(6, tag.Residual(9), "<=", 2.*tag.ResidualNegativeThreshold(), 6)
        rule3 = np.squeeze(tag.Residual(1)) <= 2.*tag.ResidualNegativeThreshold()
        return rule1 and rule2 and rule3
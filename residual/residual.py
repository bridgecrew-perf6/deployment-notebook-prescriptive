class Residual:
    def __init__(self, actual, estimate, residual_positive_threshold, residual_negative_threshold):
        self.residual = actual - estimate
        self.residual_positive_threshold = residual_positive_threshold
        self.residual_negative_threshold = residual_negative_threshold
        self.residual_indication_positive = self.get_residual_indication_positive()
        self.residual_indication_negative = self.get_residual_indication_negative()

    def get_residual_indication_negative(self):
        if self.residual < self.residual_negative_threshold:
            return 1
        elif self.residual > self.residual_negative_threshold:
            return -1
        else:
            return 0

    def get_residual_indication_positive(self):
        if self.residual > self.residual_positive_threshold:
            return 1
        elif self.residual < self.residual_positive_threshold:
            return -1
        else:
            return 0
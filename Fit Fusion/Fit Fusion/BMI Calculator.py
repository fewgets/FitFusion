class BMI:
    def __init__(self):
        self.weight_kg = 0.0
        self.height_m = 0.0
        self.height_feet = 0.0
        self.height_inches = 0.0
        self.height_total = 0.0
        self.weight_lb = 0.0

    def get_bmi_category(self, bmi):
        if bmi < 18.5:
            return "You are Underweight"
        elif 18.5 <= bmi <= 24.9:
            return "You are Normal weight"
        elif 25.0 <= bmi <= 29.9:
            return "You are Overweight"
        else:
            return "You are Suffering from obesity"


class BMIImperial(BMI):
    def __init__(self, weight_lb, height_feet, height_inches):
        super().__init__()
        self.weight_lb = weight_lb
        self.height_feet = height_feet
        self.height_inches = height_inches
        self.height_total = height_feet * 12 + height_inches

    def calculate_bmi(self):
        return (self.weight_lb / (self.height_total ** 2)) * 703


class BMIMetric(BMI):
    def __init__(self, weight_kg, height_m):
        super().__init__()
        self.weight_kg = weight_kg
        self.height_m = height_m

    def calculate_bmi(self):
        return self.weight_kg / (self.height_m ** 2)


# Example usage:
# BMI in Imperial system
bmi_imperial = BMIImperial(weight_lb=180, height_feet=5, height_inches=10)
bmi_value_imperial = bmi_imperial.calculate_bmi()
print(f"BMI (Imperial): {bmi_value_imperial:.2f}")
print(bmi_imperial.get_bmi_category(bmi_value_imperial))

# BMI in Metric system
bmi_metric = BMIMetric(weight_kg=81.65, height_m=1.78)
bmi_value_metric = bmi_metric.calculate_bmi()
print(f"BMI (Metric): {bmi_value_metric:.2f}")
print(bmi_metric.get_bmi_category(bmi_value_metric))

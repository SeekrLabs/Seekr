#from .models import Experience
from datetime import date, timedelta
from config import glove

class ExperienceRepresentation:
    def __init__(self, prev_years_lookup):
        # company2vec, title2vec, tenure length within that year
        self.prev_years_lookup = prev_years_lookup
        self.exp_map = {}

        # Add one because there is the 0th previous, current year.
        for i in range(prev_years_lookup + 1):
            self.exp_map[-i] = None

    def to_vector(self):
        res = []
        for i in range(self.prev_years_lookup):
            res += self.exp_map[-i]
        return res

    def add_experience(self, exp, profile_simulation_date):

        latest_year = profile_simulation_date.year - self.prev_years_lookup
        lower_date_bound = date(latest_year, 1, 1)

        if exp.end_date >= lower_date_bound:
            exp_title_vector = glove.get_string_embedding(exp.title, 4)
            delta_years_at_start = exp.start_date.year - profile_simulation_date.year
            delta_years_at_end = exp.end_date.year - profile_simulation_date.year

            # Experience is less than a year
            if exp.start_date.year == exp.end_date.year:
                self.update_year(exp.start_date.month, exp.end_date.month,
                        delta_years_at_start, exp_title_vector)
            
            else:
                self.update_year(exp.start_date.month, 12,
                        delta_years_at_start, exp_title_vector)
                self.update_year(1, exp.end_date.month,
                        delta_years_at_end, exp_title_vector)
                
                # Update inbetween years of start year and end year
                # Else experience is less than two years (Crosses over the year boundry)
                if exp.start_date.year + 1 != exp.end_date.year:
                    for d_year in range(delta_years_at_start+1, delta_years_at_end):
                        self.update_year(1, 12, d_year, exp_title_vector)
                
    
    def update_year(self, start_month, end_month, delta_years, exp_vector):
        month_tenured = end_month - start_month + 1
        if self.should_priortize_exp(delta_years, month_tenured):
            self.set_experience(delta_years, [month_tenured] + exp_vector)

    def should_set_experience(self, delta_years, exp_score):
        if self.exp_map[delta_years] == None or self.exp_map[delta_years][0] < exp_score:
            return True
        return False

    def set_experience(self, delta_years, exp_vector):
        self.exp_map[delta_years] = exp_vector
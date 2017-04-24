import itertools


class Recipe(object):

    def get_recipe(self, n):
        raise NotImplementedError("Recipe should implement get_recipe()")


class IdentityRecipe(Recipe):

    def get_recipe(self, n):
        return [tuple(range(n))]


class SyntheticDataRecipe(Recipe):

    def get_recipe(self, n):
        if n < 4:
            return [tuple(range(n))]
        result = []
        data = range(2,n)
        min_VFs = max(2, n-6)
        for i in xrange(min_VFs, n-1):
            new_comb = [(0,1) + i for i in itertools.combinations(data, i)]
            result.extend(new_comb)
        return result

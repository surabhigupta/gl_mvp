from data_recipe import IdentityRecipe, SyntheticDataRecipe

identity_recipe = IdentityRecipe()
synthetic_recipe = SyntheticDataRecipe()

def test_identity_data_recipe():
    assert(identity_recipe.get_recipe(1) == [(0,)])


def test_identity_data_recipe_2():
    assert(identity_recipe.get_recipe(2) == [(0,1)])


def test_identity_data_recipe_3():
    assert(identity_recipe.get_recipe(3) == [(0,1,2)])


def test_identity_data_recipe_4():
    assert(identity_recipe.get_recipe(4) == [(0,1,2,3)])


def test_identity_data_recipe_5():
    assert(identity_recipe.get_recipe(5) == [(0,1,2,3,4)])


def test_synthetic_data_recipe():
    assert(synthetic_recipe.get_recipe(1) == [(0,)])


def test_synthetic_data_recipe_2():
    assert(synthetic_recipe.get_recipe(2) == [(0,1)])


def test_synthetic_data_recipe_3():
    assert(synthetic_recipe.get_recipe(3) == [(0,1,2)])


def test_synthetic_data_recipe_4():
    assert(synthetic_recipe.get_recipe(4) == [(0,1,2,3)])


def test_synthetic_data_recipe_5():
    assert(set(synthetic_recipe.get_recipe(5)) == set([
        (0, 1, 2, 3),
        (0, 1, 2, 4),
        (0, 1, 3, 4),
        (0, 1, 2, 3, 4)
    ]))


def test_synthetic_data_recipe_6():
    assert(set(synthetic_recipe.get_recipe(6)) == set([
        (0, 1, 2, 3),
        (0, 1, 2, 4),
        (0, 1, 2, 5),
        (0, 1, 3, 4),
        (0, 1, 3, 5),
        (0, 1, 4, 5),
        (0, 1, 2, 3, 4),
        (0, 1, 2, 3, 5),
        (0, 1, 2, 4, 5),
        (0, 1, 3, 4, 5),
        (0, 1, 2, 3, 4, 5)
    ]))

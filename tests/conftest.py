import pytest
from liquidlib.liquids import Water, Glycerin, DMSO, Ethanol

@pytest.fixture
def water():
    return Water()

@pytest.fixture
def glycerin():
    return Glycerin()

@pytest.fixture
def dmso():
    return DMSO()

@pytest.fixture
def ethanol():
    return Ethanol()

@pytest.fixture
def all_liquids():
    return [Water(), Glycerin(), DMSO(), Ethanol()] 
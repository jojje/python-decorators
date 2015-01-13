from jojje.decorators import comparable
from sure import expect
import sys, os

def create_class(*decorator_args):
    @comparable(*decorator_args)
    class Person:
        def __init__(self, name, age, gender):
            self.name   = name
            self.age    = age
            self.gender = gender
        def __repr__(self):
            return "{} {} {}".format(self.name, self.age, self.gender)
    return Person

def create_people(Person):
    bobjr = Person('bob', 30, 'male')
    alice = Person('bob', 30, 'female')
    bobsr = Person('bob', 60, 'male')    
    return (bobjr, alice, bobsr)

def test_identity():
    Person = create_class('name', 'asc', 'age', 'asc')
    (bobjr, alice, bobsr) = create_people(Person)
    
    expect( bobjr ).should.eql( alice )
    expect( bobjr.__hash__() ).to.eql( alice.__hash__() )
    expect( len(set((bobjr, alice))) ).to.eql( 1 )
    expect( {bobjr: bobjr}[alice].gender ).to.eql( 'male' )
    
def test_compare():
    Person = create_class('age', 'asc', 'gender', 'asc' )
    (bobjr, alice, bobsr) = create_people(Person)
    expect( bobjr ).to.be.lower_than( bobsr )

    Person = create_class('age', 'desc', 'gender', 'asc' )
    (bobjr, alice, bobsr) = create_people(Person)
    expect( bobjr ).to.be.greater_than( bobsr )
    
    Person = create_class('name', 'asc', 'age', 'asc')
    (bobjr, alice, bobsr) = create_people(Person)    
    expect( bobjr ).to.be.lower_than( bobsr )

    Person = create_class('name', 'asc', 'age', 'desc')
    (bobjr, alice, bobsr) = create_people(Person)
    expect( bobjr ).to.be.greater_than( bobsr )

    Person = create_class('name', 'asc', 'gender', 'asc')
    (bobjr, alice, bobsr) = create_people(Person)
    expect( alice ).to.be.lower_than( bobjr )

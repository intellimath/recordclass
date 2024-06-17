from recordclass import dataobject
import dill

class Newdataclass(dataobject):
    a: float = 1.0

inputobj = Newdataclass()

does_it_pickle = dill.pickles(inputobj, byref=True)
print(does_it_pickle)

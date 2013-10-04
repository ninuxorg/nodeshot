class Attribute:
    def __init__(self,*args,**kwargs):
        self.code = kwargs['code']
        self.description = kwargs['description']
        self.datatype = kwargs['datatype']
        self.datatype_description = kwargs['datatype_description']
        self.order = kwargs['order']
        self.values= kwargs.get('values',None)
        self.required= kwargs.get('required', False)


from kamodo.util import get_defaults
from kamodo import kamodofy, Kamodo
import inspect
import importlib

import pysat
import pandas as pd

def extract_inst_kwargs(kwargs):
    """extract instrument keywords""" 
    inst_kwarg_names = get_defaults(pysat.Instrument).keys()
    inst_kwargs = {}
    for k in inst_kwarg_names:
        if k in kwargs:
            inst_kwargs[k] = kwargs.pop(k)
    return inst_kwargs


def get_instrument_doc(inst_kwargs):
    """Extracts instrument documentation from instrument module"""
    instrument_doc = ''
    
    inst_module = inst_kwargs.get('inst_module')

    if inst_module is not None:
        return inst_module.__doc__
    else:
        name = inst_kwargs.get('name')
        platform = inst_kwargs.get('platform')
        if (name is None) & (platform is None):
            raise ImportError('Need  platform and name for instrument')
        elif (name == '') & (platform == ''):
            return instrument_doc
        
        module_name = ''.join(('.', platform, '_', name))
        try:
            inst_module = importlib.import_module(module_name, 
                                                  package='pysat.instruments')
            print('loaded {}'.format(module_name))
            return inst_module.__doc__
        except:
            try:
                from pysat import user_modules
                for mod in user_modules:
                    try:
                        inst_module = importlib.import_module(mod)
                        if (inst_module.platform == platform) & (inst_module.name == name):
                            return inst_module.__doc__
                    except ImportError:
                        pass
            except ImportError:
                raise NotImplementedError('''User-registered instruments
                    not yet available in this version of pysat. 

                    Please use inst_module keyword instead''')
                pass
            raise
        return instrument_doc

def time_interpolator(timekwarg):
    """{docstring}"""

    # Note: df will be passed into this function's local scope
    # t will be provisioned as a keyword argument

    df_ = df.reindex(df.index.union(t))
    df_interpolated = df_.interpolate(method='time')
    result = df_interpolated.reindex(t)
    return result

time_interpolator_docstring = """{varname} time interpolator

parameters:
t: datetime series or list

returns: {varname} [{units}] pandas series
"""

def get_interpolator(func, varname, df, default_time, docstring):
    """Creates time interpolator with custom signature"""
    #extract source code from time_interpolator
    src = inspect.getsource(time_interpolator)

    #create variable-dependent signature
    new_src = (src \
           .format(docstring = docstring)
           .replace('timekwarg',"t = default_time")
           .replace('time_interpolator', varname))

#     default_time = self._instrument.data.index
    loc = dict(default_time = default_time, df = df)
    exec(new_src, loc)
    return loc[varname]

class Pysat_Kamodo(Kamodo):
    def __init__(self, date, **kamodo_kwargs):
        
        inst_kwargs = extract_inst_kwargs(kamodo_kwargs)

        self._citation = get_instrument_doc(inst_kwargs)
        
        self._instrument = pysat.Instrument(**inst_kwargs)

        self.load_data(pd.to_datetime(date))
        
        super(Pysat_Kamodo, self).__init__()
        
        self.register_variables()
        
        for varname, interpolator in kamodo_kwargs.items():
            self[varname] = interpolator
    
    def load_data(self, date):
        """Attempt to load data if available, else download"""
        self._instrument.load(date = date)
        if self._instrument.data.empty:
            self._instrument.download(start = date, stop = date)
            self._instrument.load(date = date)
        
    def register_variables(self):
        """register variables as kamodo functions"""
        
        for varname in self._instrument.data.columns:
            units = self._instrument.meta[varname].units
            if type(units) is not str:
                units = ''

            docstring = time_interpolator_docstring.format(varname = varname, units = units)
            interpolator = get_interpolator(time_interpolator, 
                                            varname,
                                            self._instrument.data[varname],
                                            self._instrument.data.index,
                                            docstring)

            
            self[varname] = kamodofy(interpolator, 
                                     units = units,
                                     citation = self._citation)

    @property
    def meta(self):
        """metadata of the Pysat_Kamodo interface

        meta is a python-in-heliophysics community standard"""
        return self.detail()

    @property
    def data(self):
        """Get data from underlying instrument object

        data is a python-in-heliophysics community standard"""
        # provide function-name: function data mapping
        return {self[k].__name__: self[k].data for k in self}
    
    







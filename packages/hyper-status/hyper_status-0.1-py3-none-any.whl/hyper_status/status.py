'''
> hyper_status
> Copyright (c) 2020 Xithrius
> MIT license, Refer to LICENSE for more info
'''


import datetime

from colors import colors as c


class Status:
    '''Outputs date, status and/or a custom string.'''
    
    def __init__(self, status: str, warning: str):
        self.status = status
        self.warning = warning
        self.c = {
            'fail': c['red'],
            'ready': c['green'],
            'date': c['gold'],
            'warning': c['purple'],
            'b': c['bold'],
            'u': c['underline']
        }
        
        self.insert_items()

    def catch_error(func):
        
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                print(result)

            except IndexError:
                return print(f'Color could not be found in colors.\nRun the {c["underline"]}colors{c["end"]} module to see options.')
            
            except Exception as e:
                return print(f'Fatal error occured:\n{e}')
        
        return wrapper

    def _join(self, lst: list, bind=' ') -> str:
        return bind.join(str(y) for y in lst)

    @catch_error
    def insert_items(self, e=c['end'], n=datetime.datetime.now()) -> list:
        '''

        '''
        b = self.c['b']
        n = f"{n.strftime('%b %d, %Y - %A %I:%M:%S')}{n.strftime('%p').lower()}"
        lst = [
            f"~> {b}[ {self.c['date']}{n}{e} ]{e} >",
            f"{b}[ {self.c[self.status]}{self.status.title()}{e} ]{e}:",
            f"{self.warning.capitalize()}{'.' if self.warning[-1] is not '.' else ''}"
        ]
        return self._join(lst)

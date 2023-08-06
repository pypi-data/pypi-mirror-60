import sys
from .splice import Splice
from .stream import Stream

def decode(stuff):
    '''
    All purpose SCTE 35 decoder function
    the  stuff arg can be     
         mpegts file, 
         binary file,
         base64 encoded string,
         binary encoded string, 
         hex encoded string.
     
    usage:

    # for a mpegts video 

    import threefive
    threefive.decode('/path/to/mpegts')
    
    # for a base64 encoded string

    import threefive
    Bee64='/DAvAAAAAAAA///wBQb+dGKQoAAZAhdDVUVJSAAAjn+fCAgAAAAALKChijUCAKnMZ1g='
    threefive.decode(Bee64)

    '''
    scte35=None

    if stuff==sys.stdin.buffer:  scte35=Stream(tsstream=stuff,show_null=False)
    else:
        try: 
            scte35=Splice(stuff)
            scte35.show()
        except: 
            try:  scte35=Stream(tsfile=stuff,show_null=False)
            except: pass
    return scte35

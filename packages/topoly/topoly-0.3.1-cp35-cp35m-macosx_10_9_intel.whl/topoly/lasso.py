from .invariants import Invariant
from .topoly_surfaces import c_lasso_type, c_make_surface
from .params import SurfacePlotFormat

class Lasso(Invariant):
    name = 'Lasso'

    def make_surface(self, loop_beg, loop_end, precision=0, density=1):   
        coordinates = self.get_coords()
        return c_make_surface(coordinates, loop_beg, loop_end, precision, 
                              density)   

    def lasso_type(self, loop_beg, loop_end,                                  
                   smoothing=0, step=1, precision=0, dens=1, min_dist=10, 
                   min_bridge_dist=3, min_tail_dist=10, 
                   pic_files=SurfacePlotFormat.DONTPLOT, output_prefix='', 
                   output_type=1): 
        coordinates = self.get_coords()
        if pic_files == None:                                                        
            pic_files = 0                                                            
        elif type(pic_files) == int:                                                 
            pass                                                                     
        elif type(pic_files) == list:                                                
            summ = 0                                                                 
            for ext in pic_files:                                                    
                summ += ext                                                          
            pic_files = summ                                                         
        pic_files = int(bin(pic_files)[2:])                                          
        return c_lasso_type(coordinates, loop_beg, loop_end, smoothing, step,        
                      precision, dens, min_dist, min_bridge_dist, min_tail_dist,   
                      pic_files, output_prefix.encode('utf-8'), output_type)

    #TODO
    def lasso_classify(self, loop_indices, smoothing=0, step=1,
             precision=0, dens=1, min_dist=10, min_bridge_dist=3,            
             min_tail_dist=1, pic_files=SurfacePlotFormat.DONTPLOT, 
             output_prefix='', output_type=1): 
        coordinates = self.get_coords()
        out = []                                                                     
        for pair in loop_indices:                                                    
            loop_beg, loop_end = pair                                                
            out.append(lasso_type(coordinates, loop_beg, loop_end, smoothing,
                       step,precision, dens, min_dist, min_bridge_dist, min_tail_dist,    
                       pic_files, output_prefix, output_type))                       
        return '\n'.join(out)  

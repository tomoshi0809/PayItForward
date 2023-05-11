import numpy as np

class Item:
    def __init__(self, _id, param):
        self.id = _id
        self.vec_len = param['vec_len']
        self.vec_sig = param['vec_sig']
        self.vec_mean = param['vec_mean']
        self.vector = np.clip(np.random.normal(self.vec_mean, self.vec_sig, self.vec_len), 0, 1)
        
        self.price = param['price']
        self.purchase_cntr = 0
        
    def purchase_cntr_zero(self):
        self.purchase_cntr = 0
        
    def purchase_cntrup(self):
        self.purchase_cntr += 1
        
    def decrement_price(self, decrement):
        self.price -= decrement
        if self.price < 0:
            self.price = 0
            
    def set_vector(self, vector):
        assert len(vector) == self.vec_len
        self.vector = vector
from customer import Customer
from item import Item

class Store:
    def __init__(self, param):
        self.item_id_cntr = 0
        self.param = param
        self.n_items = param['n_items']
        self.n_customers = param['n_customers']
        self.items = self.create_new_items(self.n_items, param['item_param'], self.item_id_cntr)
        self.customers = {id_ : Customer(id_, param['customer_param'], self) for id_ in range(self.n_customers)}

    def purchase(self, item):
        self.items[item.id].purchase_cntrup()
    
    def get_items(self):
        return self.items
    
    def get_customers(self):
        return self.customers
    
    def pf(self, item, pf_unit):
        #print("PF to ", item.id)
        item.decrement_price(pf_unit)
    
    def has_item(self, item):
        return item.id in list(self.items.keys())
    
    def get_remain_items(self, items, n):
        return dict(sorted(items.items(), key = lambda x: x[1].purchase_cntr, reverse = True)[:n])
    
    def create_new_items(self, n, item_param, first_id):
        self.item_id_cntr += n
        return {first_id + id_ : Item(first_id + id_, item_param) for id_ in range(n)}
    
    def replace_n_items (self, n):
        tmp = self.get_remain_items(self.items, self.n_items - n)
        tmp.update(self.create_new_items(n, self.param['item_param'], self.item_id_cntr))
        self.items = tmp
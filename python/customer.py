import numpy as np
import random

def cos_sim(v1, v2):
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

class Customer:
    def __init__(self, _id, param, store):
        self.store = store
        self.id = _id
        
        self.vec_len = param['vec_len']
        self.vec_sig = param['vec_sig']
        self.vec_mean = param['vec_mean']
        self.vector = np.clip(np.random.normal(self.vec_mean, self.vec_sig, self.vec_len), 0, 1)
        self.pf_unit = param['pf_unit']
        
        self.exp_benefit_dict = dict()
        self.prob_dict = dict()

        self.exp_benefit_dict['item'] = {'n' : 0, 'mean' : 0}
        self.exp_benefit_dict['noitem'] = {'n' : 0, 'mean' : 0}
    
        self.prob_dict['item_pf'] = {'n' : 0, 'mean' : 0}
        self.prob_dict['noitem_pf'] = {'n' : 0, 'mean' : 0}
        self.prob_dict['item_nopf'] = {'n' : 0, 'mean' : 0}
        self.prob_dict['noitem_nopf'] = {'n' : 0, 'mean' : 0}
        
        self.epsilon = param['epsilon']
        self.epsilon_pf = param['epsilon_pf']
        self.item_reward_dict = dict()
        self.is_pf_prev = False
        self.budget = 0
        
        self.step = 0
    
    def set_vector(self, vector):
        assert len(vector) == self.vec_len
        self.vector = vector
    
    # 購入候補となる商品の選択
    def select_item(self, cur_best_item, items):
        if cur_best_item is not None and not(self.store.has_item(cur_best_item)):
            return random.choice(items), 'no_cur_best_item'
        
        if cur_best_item is None or random.random() < self.epsilon: #新規探求
            return random.choice(items), 'novelty'
        else:
            return cur_best_item, 'cur_best_item'
    
    def is_purchase(self, item):
        if self.calc_benefit(item) > 0:
            return True
        else:
            return False
    
    def is_pf (self, beta, alpha, exp_benefit_item, exp_benefit_noitem, cur_purchase_item, pf_unit, epsilon):
        if random.random() < epsilon or (beta - alpha) * exp_benefit_item - (beta - alpha) * exp_benefit_noitem >= pf_unit:
            return True
        else:
            return False

    #rewardはベクトル同士のcos類似度によって計算される利益、benefitは、rewardから値段を引いた値と定義
    def calc_benefit (self, item):
        if item is None:
            return 0
        
        return cos_sim(self.vector, item.vector) - item.price
    
    def test_calc_benefit (self):
        item = Item(0, item_param)
        item.price = 0.01
        customer = Customer(0, customer_param)
        item.vector = [1, 2, 1]
        customer.vector = [1, 2, 1]
        
        assert customer.calc_benefit(None) == 0
        assert customer.calc_benefit(item) == 0.99
    
    def update_mean (self, n, mean, new_value):
        return n + 1, mean + float (new_value - mean)/(n+1)
    
    def test_update_mean (self):
        assert self.update_mean(5, 1, 7) == 2
    
    # benefitは、購入してみないとわからない、という方式でとりあえずやってみる
    def process (self):
        cur_items = self.store.get_items()
        # 最大報酬およびその商品を取得（この商品が存在するかは不明）
        if len(self.item_reward_dict) > 0:
            cur_best_item = max(self.item_reward_dict.items(), key = lambda x:x[1] - x[0].price)[0] # 経験的に取得するrewardから価格を引く
        else:
            cur_best_item = None

        item, res = self.select_item(cur_best_item, cur_items)
        
        if res == 'no_cur_best_item':
            # メモリから消す        
            del self.item_reward_dict[cur_best_item]
            if self.is_pf_prev: # 前回PFしており、今回商品がない
                _n = self.prob_dict['noitem_pf']['n']
                _mean = self.prob_dict['noitem_pf']['mean'] 
                self.prob_dict['noitem_pf']['n'], self.prob_dict['noitem_pf']['mean'] = self.update_mean(_n, _mean, 0)
            else: # 前回PFしておらず、今回商品がない
                _n = self.prob_dict['noitem_nopf']['n']
                _mean = self.prob_dict['noitem_nopf']['mean'] 
                self.prob_dict['noitem_nopf']['n'], self.prob_dict['noitem_pf']['mean'] = self.update_mean(_n, _mean, 0)
            
        else:
            if self.is_pf_prev: # 前回PFしており、今回商品がある
                _n = self.prob_dict['item_pf']['n']
                _mean = self.prob_dict['item_pf']['mean'] 
                self.prob_dict['item_pf']['n'], self.prob_dict['item_pf']['mean'] = self.update_mean(_n, _mean, 1)
            else: # 前回PFしておらず、今回商品がある
                _n = self.prob_dict['item_nopf']['n']
                _mean = self.prob_dict['item_nopf']['mean'] 
                self.prob_dict['item_nopf']['n'], self.prob_dict['item_nopf']['mean'] = self.update_mean(_n, _mean, 1)
        
        # 購入決定
        if self.is_purchase (item):
            self.store.purchase (item)
            self.cur_purchase_item = item
        else:
            self.cur_purchase_item = None
        
        benefit = self.calc_benefit(self.cur_purchase_item)
        self.budget = self.budget + benefit
        #import pdb; pdb.set_trace()
        
        # 期待値更新
        if res == 'no_cur_best_item':
            _n = self.exp_benefit_dict['noitem']['n']
            _mean = self.exp_benefit_dict['noitem']['mean']
            self.exp_benefit_dict['noitem']['n'], self.exp_benefit_dict['noitem']['mean'] = self.update_mean(_n, _mean, benefit)
        else:
            _n = self.exp_benefit_dict['item']['n']
            _mean = self.exp_benefit_dict['item']['mean']
            self.exp_benefit_dict['item']['n'], self.exp_benefit_dict['item']['mean'] = self.update_mean(_n, _mean, benefit)
        
        # メモリ更新
        self.item_reward_dict[self.cur_purchase_item] = benefit
        
        # PF決定と予算更新
        if self.is_pf(beta = self.prob_dict['item_pf']['mean'], alpha = self.prob_dict['item_nopf']['mean'],\
                      exp_benefit_item = self.exp_benefit_dict['item']['mean'], exp_benefit_noitem = self.exp_benefit_dict['noitem']['mean'], \
                      cur_purchase_item = self.cur_purchase_item, pf_unit = self.pf_unit, epsilon = self.epsilon_pf):
        
            self.store.pf(self.cur_purchase_item, self.pf_unit)
            self.budget -=  self.pf_unit
            self.is_pf_prev = True
        else:
            self.is_pf_prev = False
        
        self.step += 1
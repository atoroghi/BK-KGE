import torch
import torch.nn as nn
import numpy as np
import torch.nn.functional as F

class SimplE(nn.Module):
    def __init__(self, num_ent, num_rel, emb_dim, reg_lambda, device):
        super(SimplE, self).__init__()
        self.num_ent = num_ent
        self.num_rel = num_rel
        self.emb_dim = emb_dim
        self.reg_lambda = reg_lambda
        self.device = device

        self.ent_h_embs   = nn.Embedding(self.num_ent, emb_dim).to(device)
        self.ent_t_embs   = nn.Embedding(self.num_ent, emb_dim).to(device)
        self.rel_embs     = nn.Embedding(self.num_rel, emb_dim).to(device)
        self.rel_inv_embs = nn.Embedding(self.num_rel, emb_dim).to(device)

        sqrt_size = 6.0 / np.sqrt(self.emb_dim)
        nn.init.uniform_(self.ent_h_embs.weight.data, -sqrt_size, sqrt_size)
        nn.init.uniform_(self.ent_t_embs.weight.data, -sqrt_size, sqrt_size)
        nn.init.uniform_(self.rel_embs.weight.data, -sqrt_size, sqrt_size)
        nn.init.uniform_(self.rel_inv_embs.weight.data, -sqrt_size, sqrt_size)
        
    def forward(self, heads, rels, tails):
        hh_embs = self.ent_h_embs(heads)
        ht_embs = self.ent_h_embs(tails)
        th_embs = self.ent_t_embs(heads)
        tt_embs = self.ent_t_embs(tails)
        r_embs = self.rel_embs(rels)
        r_inv_embs = self.rel_inv_embs(rels)

        for_prod = torch.sum(hh_embs * r_embs * tt_embs, dim=1)
        inv_prod = torch.sum(ht_embs * r_inv_embs * th_embs, dim=1)

        return torch.clamp((for_prod + inv_prod) / 2, -20, 20) 

    def loss(self, score, labels):
        out = F.softplus(-labels * score)
        loss = torch.sum(out)
        return loss

    def reg_loss(self):
        norm_val = ((torch.norm(self.ent_h_embs.weight, p=2) ** 2) \
            + (torch.norm(self.ent_t_embs.weight, p=2) ** 2) \
            + (torch.norm(self.rel_embs.weight, p=2) ** 2) \
            + (torch.norm(self.rel_inv_embs.weight, p=2) ** 2)
        )
        return norm_val

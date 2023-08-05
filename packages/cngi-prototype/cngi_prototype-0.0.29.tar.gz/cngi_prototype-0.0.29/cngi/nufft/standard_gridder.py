#   Copyright 2019 AUI, Inc. Washington DC, USA
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
import numpy as np
from numba import jit
import time
import math

def _convert_sum_weight_to_sparse(sum_weight,n_chan,n_pol,n_uv):
     import sparse
     
     sum_weight_coords = np.zeros((4,n_chan*n_pol),dtype=int)
     sum_weight_data = np.zeros((n_chan*n_pol),dtype=np.float64)
     flat_indx = 0
     for i_chan in range(n_chan):
       for i_pol in range(n_pol):
         sum_weight_coords[0,flat_indx] = i_chan
         sum_weight_coords[1,flat_indx] = i_pol
         sum_weight_data[flat_indx] = sum_weight[i_chan,i_pol]
         flat_indx = flat_indx + 1
     return sparse.COO(sum_weight_coords, sum_weight_data, shape=(n_chan,n_pol,n_uv[0],n_uv[1]))


def standard_grid_dask_sparse(vis_data, uvw, weight, flag_row, flag, freq_chan, cgk_1D, grid_parms):
      """
      Wrapper function that is used when using dask distributed parallelism (blockwise function). 
      
      Parameters
      ----------
      vis_data : complex array
          (n_time, n_baseline, n_chan, n_pol)
      uvw  : float array
          (n_time, n_baseline, 3)
      weight : float array 
          (n_time, n_baseline, n_vis_chan)
      flag_row : boolean array 
          (n_time, n_baseline)
      flag : boolean array 
          (n_time, n_baseline, n_chan, n_pol)
      freq_chan : float array
          (n_chan)
      cgk_1D : float array 
          (oversampling*(support//2 + 1))
      grid_parms : dictionary 
          ('imsize','cell','oversampling','support')

      Returns
      -------
      grid : complex sparse array 
          (1,2,n_imag_chan,n_imag_pol,n_u,n_v)
          grid[0,0,0,0,:,:,:,:,0] contains gridded data
          grid[0,0,0,0,:,:,0,0,1] contains the sum of weights.
      """
      
      import sparse
      n_chan = vis_data.shape[2]
      if grid_parms['chan_mode'] == 'cube':
          n_imag_chan = n_chan  
          chan_map = (np.arange(0,n_chan)).astype(np.int) 
      else: #continuum
          n_imag_chan = 1  # Making only one continuum image.
          chan_map = (np.zeros(n_chan)).astype(np.int) 
      
      n_imag_pol = vis_data.shape[3]
      pol_map = (np.arange(0,n_imag_pol)).astype(np.int) 
      
      n_uv = grid_parms['imsize']
      delta_lm = grid_parms['cell']
      oversampling = grid_parms['oversampling']
      support = grid_parms['support']
     
      grid = np.zeros((n_imag_chan, n_imag_pol, n_uv[0],n_uv[1]),dtype=np.complex128)
      sum_weight = np.zeros((n_imag_chan, n_imag_pol),dtype=np.double)
     
      _standard_grid_jit(grid, sum_weight, vis_data, uvw[0], freq_chan, chan_map, pol_map, weight, flag_row,flag, cgk_1D, n_uv, delta_lm, support, oversampling)
      
      sum_weight = _convert_sum_weight_to_sparse(sum_weight,n_imag_chan,n_imag_pol,n_uv)
      #The first 4 Nones are the chunking dimentions that the blockwise function needs. 
      #The Last None is for the switching variable between the grid and the sum_weights.
      sum_weight = sum_weight[None,None,None,None,:,:,:,:,None]
      grid = sparse.COO(grid[None,None,None,None,:,:,:,:,None]) 
      grid_and_sum_weight = sparse.concatenate((grid,sum_weight),axis=8)
      
      return grid_and_sum_weight


@jit(nopython=True,cache=True)
def _standard_grid_jit(grid, sum_weight, vis_data, uvw, freq_chan, chan_map, pol_map, weight, flag_row, flag, cgk_1D, n_uv, delta_lm, support, oversampling):
      """
      Parameters
      ----------
      grid : complex array 
          (n_chan, n_pol, n_u, n_v)
      sum_weight : float array 
          (n_chan, n_pol) 
      vis_data : complex array 
          (n_time, n_baseline, n_vis_chan, n_pol)
      uvw  : float array 
          (n_time, n_baseline, 3)
      freq_chan : float array 
          (n_chan)
      chan_map : int array 
          (n_chan)
      pol_map : int array 
          (n_pol)
      weight : float array 
          (n_time, n_baseline, n_vis_chan)
      flag_row : boolean array 
          (n_time, n_baseline)
      flag : boolean array 
          (n_time, n_baseline, n_chan, n_pol)
      cgk_1D : float array 
          (oversampling*(support//2 + 1))
      grid_parms : dictionary 
          keys ('n_imag_chan','n_imag_pol','n_uv','delta_lm','oversampling','support')

      Returns
      -------
      """
      
      c = 299792458.0
      uv_scale = np.zeros((2,len(freq_chan)), dtype=np.double)
      uv_scale[0,:] = (freq_chan*delta_lm[0]*n_uv[0])/c
      uv_scale[1,:] = (freq_chan*delta_lm[1]*n_uv[1])/c
      

      oversampling_center =  int(oversampling//2)
      support_center = int(support//2)
      uv_center = n_uv//2
      
      n_time = uvw.shape[0]
      n_baseline = uvw.shape[1]
      n_chan = len(chan_map)
      n_pol = len(pol_map)
      n_imag_chan = chan_map.shape[0]
      
      
      n_u = n_uv[0]
      n_v = n_uv[1]
      
      for i_time in range(n_time):
        for i_baseline in range(n_baseline):
          if flag_row[i_time,i_baseline] == 0:
            for i_chan in range(n_chan): 
              a_chan = chan_map[i_chan]
            
              if a_chan >= 0 and a_chan < n_imag_chan: 
                u =  -uvw[i_time,i_baseline,0]*uv_scale[0,i_chan]
                v =  -uvw[i_time,i_baseline,1]*uv_scale[1,i_chan]
                u_pos = u + uv_center[0]
                v_pos = v + uv_center[1]
                u_center_indx = int(u_pos + 0.5) 
                v_center_indx = int(v_pos + 0.5)
              
                if u_center_indx < n_u and v_center_indx < n_v and u_center_indx >= 0 and v_center_indx >= 0:
                  u_offset = u_center_indx - u_pos 
                  u_center_offset_indx = math.floor(u_offset*oversampling + 0.5)
                  v_offset = v_center_indx - v_pos
                  v_center_offset_indx = math.floor(v_offset*oversampling + 0.5)
                
                
                  for i_pol in range(n_pol):
                    if weight[i_time,i_baseline,i_pol] != 0.0:
                      a_pol=pol_map[i_pol]
                      weigted_data  = vis_data[i_time,i_baseline,i_chan,i_pol]*weight[i_time,i_baseline,i_pol]
                      norm = 0.0
                    
                      if flag[i_time,i_baseline,i_chan,i_pol] == 0:
                        for i_v in range(-support_center,support_center+1):
                          v_indx = v_center_indx + i_v
                          v_offset_indx = np.abs(oversampling*i_v + v_center_offset_indx)
                          conv_v = cgk_1D[v_offset_indx]
                        
                          for i_u in range(-support_center,support_center+1):
                            u_indx = u_center_indx + i_u
                            u_offset_indx = np.abs(oversampling*i_u + u_center_offset_indx)
                            conv_u = cgk_1D[u_offset_indx]
                            conv = conv_u * conv_v
                        
                            grid[a_chan,a_pol,u_indx,v_indx] = grid[a_chan,a_pol,u_indx,v_indx] + conv*weigted_data
                            norm = norm + conv
                          
                      sum_weight[a_chan,a_pol] = sum_weight[a_chan,a_pol] + weight[i_time,i_baseline,i_pol]*norm               
                  
      return
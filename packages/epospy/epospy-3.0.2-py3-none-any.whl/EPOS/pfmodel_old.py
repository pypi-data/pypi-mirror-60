import glob
import numpy as np
import sys, os

from . import cgs

''' Helper functions to read in planet formation models'''

def bern(name='syntheticpop_20emb_983systems.txt', dir='Bern', 
		smacut=[0,np.inf], masscut= [0,np.inf], Rcut=[0,np.inf], 
		Verbose=False, Single=False):
	fname= '{}/{}'.format(dir,name)

	''' Read the header '''
	header= np.genfromtxt(fname, max_rows=1, dtype=str, delimiter=',')
	if Verbose:
		print ('\nColumns:')
		for k, colname in enumerate(header):
			print ('  a[{}]: {}'.format(k, colname))

	''' Read the data '''
	a= np.loadtxt(fname, unpack=True, skiprows=1)
	if Verbose:
		print ('\nraw data: {} systems, {} planets'.format(np.unique(
			a[0 if Single else 1]).size, a[0].size))

	# cut out certain planets
	include= (smacut[0]<=a[2]) & (a[2]<=smacut[-1])
	include&= (masscut[0]<=a[3]) & (a[3]<=masscut[-1])
	include&= (Rcut[0]<=a[4]) & (a[4]<=Rcut[-1])
	#include&= (cut[0]<=a[]) & (a[]<=cut[-1])

	#planet= a[0][include]
	ID= a[0 if Single else 1][include]
	sma= a[2][include]
	mass= a[3][include]
	radius= a[4][include]
	ecc= a[5][include]
	inc=a[6][include] * (180./np.pi) # rad -> degrees
	FeH= a[7][include]
	Mcore= a[8][include]
	Menv= a[9][include]
	sma0= a[10][include]
	fice= a[11][include]

	print ('\nLoad population synthesis model {}'.format(name))
	print ('  included {} systems, {} planets'.format(np.unique(ID).size, sma.size))
	print ('  sma:  	 {:.2e} ... {:.1f}'.format(min(sma), max(sma)))
	print ('  sma0: 	 {:.2e} ... {:.1f}'.format(min(sma0), max(sma0)))
	print ('  mass:   {:.2e} ... {:.1f}'.format(min(mass), max(mass)))
	print ('  radius: {:.2f} ... {:.1f}'.format(min(radius), max(radius)))
	print ('  inc:    {:.2e} ... {:.1f}'.format(min(inc), max(inc)))
	print ('  Fe/H:   {:.2f} ... {:.2f}'.format(min(FeH), max(FeH)))
	
	order= np.lexsort((sma,ID)) 
	
	npz={'sma':sma[order], 'mass':mass[order], 'radius':radius[order], 
		'inc':inc[order], 'ecc':ecc[order], 'starID':ID[order], 
		'Mcore':Mcore[order], 'Menv':Menv[order], 'fice':fice[order],
		'tag':FeH[order], 'sma0':sma0[order]}
	
	if Single: npz['inc']=None

	return npz

def morby(name, fname, Verbose=False, Saved=True):
	''' 
	returns a list of planetary systems
	sma in au
	mass in earth masses
	'''
	
	dir= 'npz/{}'.format(name)
	if not os.path.exists(dir): os.makedirs(dir)
	fnpz= '{}/{}.npz'.format(dir, name)	
	
	''' Load hdf5 file or npz dictionary for quicker access'''
	if os.path.isfile(fnpz) and Saved:
		print ('\nLoading saved status from {}'.format(fnpz))
		npz= np.load(fnpz)
				
		# check if keys present
		for key in ['sma','mass','inc','starID']:
			if not key in npz: 
				raise ValueError('Key {} not present\n{}'.format(key,npz.keys()))
	else:
		print ('\nProcessing Symba HDF5 file for {}'.format(name))
		#fname= '{}/{}_set??.h5'.format(dir,name)
		flist= glob.glob(fname)
		if len(flist)==0: 
			raise ValueError('file not found: {}'.format(fname))
		else:
			if Verbose: print ('  {} files'.format(len(flist)))
	
		sma, mass, inc, ecc, ID= [], [], [], [], []
	
		for i,fname in enumerate(flist):
			a= np.loadtxt(fname,skiprows=1, usecols=(1,2,3,7), unpack=True)
			#if a.ndim==1: a=[a]
			try:
				if a.ndim==1:
					sma.append([a[0]])
					ecc.append([a[1]])
					inc.append([a[2]])
					mass.append([a[3]])

					ID.append([i])
				elif a.ndim==2:

					sma.append(a[0])
					ecc.append(a[1])
					inc.append(a[2])
					mass.append(a[3])

					ID.append([i]*len(a[0]))
				else:
					print (a.shape)
					print (a)
					raise ValueError('Error reading in') 
			except (IndexError, TypeError):
				print (a.shape)
				print (a)
				raise

			# print (system properties:
			if Verbose:
				print ('System {} has {} planets, {:.1f} Mearth:'.format(
					i, len(sma[-1]),np.sum(mass[-1])))
				for items in zip(sma[-1], mass[-1], inc[-1]):
					print ('  {:.2f} au, {:.1f} Mearth, {:.3g} deg'.format(*items))
		
		npz={'sma':np.concatenate(sma), 'mass':np.concatenate(mass), 
			'inc':np.concatenate(inc), 'starID':np.concatenate(ID),
			'ecc':np.concatenate(ecc)}
		
		if Saved:
			print ('Saving status in {}'.format(fnpz))
			#np.save(fname, epos.chain)
			# compression slow on loading?
			np.savez_compressed(fnpz, **npz)
		
	return npz


def mordasini(name='syntheticpopmordasini1MsunJ31', dir='Mordasini', smacut=np.inf,
		Rcut=0, Single=False, Verbose=False):
	fname= '{}/{}.dat'.format(dir,name)
	header= np.genfromtxt(fname, max_rows=1, dtype=str)
	print (header)
	a= np.loadtxt(fname, unpack=True, skiprows=1, usecols=(0,1,2,3,4,6,7))

	npl= a[2].size
	ns= np.unique(a[0 if Single else 1]).size

	include= (a[2]<smacut) & (a[4]>Rcut)
	ID= a[0 if Single else 1][include]
	sma= a[2][include]
	mass= a[3][include]
	radius= a[4][include]
	inc=a[5][include]
	FeH= a[6][include]

	print ('\nLoad population synthesis model {}'.format(name))
	print ('  {} stars, {} planets'.format(ns, npl))
	print ('  sma:  	 {:.2e} ... {:.1f}'.format(min(sma), max(sma)))
	print ('  mass:   {:.2e} ... {:.1f}'.format(min(mass), max(mass)))
	print ('  radius: {:.2f} ... {:.1f}'.format(min(radius), max(radius)))
	print ('  inc:    {:.2e} ... {:.1f}'.format(min(inc), max(inc)))
	print ('  Fe/H:   {:.2f} ... {:.2f}'.format(min(FeH), max(FeH)))
	
	order= np.lexsort((sma,ID)) 
	
	npz={'sma':sma[order], 'mass':mass[order], 'radius':radius[order], 
		'inc':inc[order], 'starID':ID[order], 'tag':FeH[order]}

	if Single: npz['inc']=None
		
	return npz

def mordasini_ext(name='syntheticpopmordasini1MsunJ31extended', dir='Mordasini', smacut=np.inf,
		Rcut=0, Verbose=False):
	fname= '{}/{}.dat'.format(dir,name)
	header= np.genfromtxt(fname, max_rows=1, dtype=str)
	print (header)
	a= np.loadtxt(fname, unpack=True, skiprows=1, usecols=(1,2,3,4,6,7,10))

	npl= a[2].size
	ns= np.unique(a[0 if Single else 1])

	include= (a[1]<smacut) & (a[3]>Rcut)
	ID= a[0][include]
	sma= a[1][include]
	mass= a[2][include]
	radius= a[3][include]
	inc=a[4][include]
	FeH= a[5][include]
	sma0= a[6][include]

	print ('\nLoad population synthesis model {}'.format(name))
	print ('  {} stars, {} planets'.format(ns, npl))
	print ('  sma:  	 {:.2e} ... {:.1f}'.format(min(sma), max(sma)))
	print ('  sma0: 	 {:.2e} ... {:.1f}'.format(min(sma0), max(sma0)))
	print ('  mass:   {:.2e} ... {:.1f}'.format(min(mass), max(mass)))
	print ('  radius: {:.2f} ... {:.1f}'.format(min(radius), max(radius)))
	print ('  inc:    {:.2e} ... {:.1f}'.format(min(inc), max(inc)))
	print ('  Fe/H:   {:.2f} ... {:.2f}'.format(min(FeH), max(FeH)))
	
	order= np.lexsort((sma,ID)) 
	
	npz={'sma':sma[order], 'mass':mass[order], 'radius':radius[order], 
		'inc':inc[order], 'starID':ID[order], 'tag':FeH[order], 'sma0':sma0[order]}
		
	return npz

def combine(pfmlist, tags):
	''' Combine Multiple Planet Formation Model'''
	assert len(tags) == len(pfmlist)

	''' Create list of tags '''
	taglist= []
	for pfm, tag in zip(pfmlist, tags):
		taglist.append(np.full_like(pfm['sma'], tag))

	''' Create merged dictionary'''
	npz={'tag':np.concatenate(taglist)}
	for key in pfm.keys():
		npz[key]= np.concatenate([pfm[key] for pfm in pfmlist])

	return npz
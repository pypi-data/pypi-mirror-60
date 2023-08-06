import pandas as pd
class OutRem:
	def __init__(self,filename,header=None):
		self.data = pd.read_csv(filename,header=header)
		self.head = self.data.iloc[0,:].values
		self.d = self.data.iloc[1:,:].values
		self.d = self.d.astype('float64')
		self.outlier_tuples = []
		self.features = len(self.d[0])
		self.samples = len(self.d)
	def generateOutputFile(self,outfilename='out.csv'):
		for i in range(0,self.features):
			k = self.d[:,i]
			self.sorted_k = sorted(k)
			samples = self.samples
			self.median = (samples+1)//2
			self.q1 = (samples+1)//4
			self.q3 = (3*(samples+1))//4
			if self.median == (samples+1)/2:
				self.median = self.sorted_k[self.median-1]+((self.sorted_k[(self.median)]-self.sorted_k[self.median-1])*(((samples+1)/2)-self.median))
			else:
				self.median = self.sorted_k[self.median-1]
			if self.q1 == (samples+1)/4:
				self.q1 = self.sorted_k[self.q1-1]+((self.sorted_k[(self.q1)]-self.sorted_k[self.q1-1])*(((samples+1)/4)-self.q1))
			else:
				self.q1 = self.sorted_k[self.q1-1]
			if self.q3 == 3*(samples+1)/4:
				self.q3 = self.sorted_k[self.q3-1]+((self.sorted_k[(self.q3)]-self.sorted_k[self.q3-1])*((3*(samples+1)/4)-self.q3))
			else:
				self.q3 = self.sorted_k[self.q3-1]
			self.iqr = self.q3-self.q1
			self.minn = self.q1 - (1.5*self.iqr)
			self.maxx = self.q3 + (1.5*self.iqr)
			for j in range(0,samples):
				if self.d[j,i]>self.maxx or self.d[j,i]<self.minn:
					self.outlier_tuples.append(j)
		self.outlier_tuples = list(set(self.outlier_tuples))    	
		self.d = pd.DataFrame(self.d,columns=self.head)
		self.d = self.d.drop(self.outlier_tuples)
		self.d.to_csv(outfilename,index=False)

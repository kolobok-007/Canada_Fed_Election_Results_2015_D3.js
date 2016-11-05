# -*- coding: utf-8 -*-
"""
@author: mvenkov
"""
def process_election_results(input_file,output_file):
	import pandas as pd
	results_df = pd.read_csv (input_file,sep='\t')
	print results_df.columns
	# print results_df.groupby('Type of results*').count()

	results_df=results_df[results_df['Type of results*'].isin(['judicially certified','validated'])]

	max_ids = results_df.groupby('Electoral district number - Numéro de la circonscription')['% Votes obtained - Votes obtenus %'].idxmax()

	max_df = results_df.loc[max_ids]

	max_df = pd.DataFrame ({'num':max_df['Electoral district number - Numéro de la circonscription'],
							# 'lastname_w':max_df['Surname - Nom de famille'],
							# 'firstname_w':max_df['Given name - Prénom'],
							'fullname_w':max_df['Given name - Prénom']+' '+max_df['Given name - Prénom'],
							'party_w':max_df['Political affiliation'],
							'percentvotes_w':max_df['% Votes obtained - Votes obtenus %']
							})
	rename_dict = {'Electoral district number - Numéro de la circonscription':'num',
					'Electoral district name':'District Name',
					'Surname - Nom de famille':'Last Name',
					'Given name - Prénom': 'First Name',
					'Political affiliation':'Party',
					'% Votes obtained - Votes obtenus %':'Percent Votes'
					}
	results_df.rename(columns=rename_dict,inplace=True)

	final_df = results_df.merge(max_df, on='num')

	final_df['Full Name']=final_df['First Name']+' '+final_df['Last Name']

	final_df=final_df[['num','District Name','Full Name','Party','Percent Votes','fullname_w','party_w','percentvotes_w']]

	final_df.to_csv(output_file,index=False)

def to_str(table):
	# encodes a table into a str file
	name=None
	output=[]
	for row in table:
		name = row[1]
		if isinstance(name,unicode):
			row[1]=name.encode('utf-8')
		output.append(row)
	return output

if __name__=='__main__':
	import csv
	import os
	
	folder =os.path.dirname(os.path.realpath(__file__))+r'\\data\\'
	results_file = folder+'EventResults.txt'
	output_file = folder + 'Results_Processed.csv'
	process_election_results(results_file,output_file)

	print 'Finished executing'


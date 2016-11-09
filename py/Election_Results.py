# -*- coding: utf-8 -*-
"""
@author: mvenkov
"""
def process_election_results(input_file,output_file,prov_map_file):
	import pandas as pd
	results_df = pd.read_csv (input_file,sep='\t')
	prov_map_df = pd.read_csv (prov_map_file)

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
					'% Votes obtained - Votes obtenus %':'Percent Votes',
					'Votes obtained - Votes obtenus':'Votes'
					}
	results_df.rename(columns=rename_dict,inplace=True)

	final_df = results_df.merge(max_df, on='num')



	final_df['Full Name']=final_df['First Name']+' '+final_df['Last Name']
	
	final_df['Percent Trailing']=final_df['percentvotes_w']-final_df['Percent Votes']
	min_ids=final_df[final_df['Percent Trailing']!=0].groupby('num')['Percent Trailing'].idxmin()
	min_df = final_df.loc[min_ids]
	min_df=min_df[['num','Percent Trailing']]
	min_df.columns=['num','Closest Trailing']

	################
	#Create a summary
	actual_won_df = final_df.groupby('party_w')['num'].nunique()
	total_seats = actual_won_df.sum()
	per_won_df=actual_won_df/total_seats*100

	winning_parties = actual_won_df.index
	total_votes=final_df['Votes'].sum()
	
	
	def check_winning_party(x): 
		if x in winning_parties:
			return x
		else:
			return 'Other'

	final_df['Party (group)']=final_df['Party'].apply(check_winning_party)

	per_votes_df = final_df.groupby('Party (group)')['Votes'].sum()/total_votes*100
	pop_seats_df = per_votes_df*total_seats/100

	summary_df = pd.DataFrame({'Seats Won':actual_won_df,
							   'Percent of Seats':per_won_df,
							   'Percent of Votes':per_votes_df,
							   'Seats based on Votes':pop_seats_df
								})

	# print summary_df


	final_df = final_df[['num','District Name','Full Name','Party','Percent Votes','fullname_w','party_w','percentvotes_w']]
	final_df = final_df.merge(prov_map_df,on='num')
	final_df = final_df.merge(min_df, on='num')
	
	
	
	summary_df.to_csv(output_file+'summary.csv')
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
	prov_map_file = folder + 'Prov Mapping.csv'

	process_election_results(results_file,output_file,prov_map_file)

	print 'Finished executing'


import pandas

def shift_df_column(df_og, attribute, new_pos=0, axis=0):
	# move total points column
	attribute_series = df_og[attribute]
	df_new = df_og.drop(attribute, axis=axis)
	df_new.insert(loc=new_pos, column=attribute, value=attribute_series)

	return df_new
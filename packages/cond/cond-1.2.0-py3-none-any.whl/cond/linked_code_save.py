satisfies_linked_cond = True

#for every linked cond object passed
for linked_cond in variables_to_cond.values():
	if type(linked_cond) is LinkedCond:
		#loop through all its limitations
		for limitation in linked_cond._getLimsRepr():
			#interpret the limitations as a formula
			lim_formula = _interpretExpression(limitation[0], len(limitation[1]))
			#map variables of limitation expression to corresponding Cond objects
			lim_variables_to_cond = _mapVariablesToCond(limitation[0], limitation[1])
			#get the variable which represents the LinkedCond object in expression
			for cond_variable in lim_variables_to_cond:
				if lim_variables_to_cond[cond_variable] is linked_cond:
					linked_cond_variable = cond_variable
					break
			#get the current value of the LinkedCond object
			linked_cond_value = linked_cond[indexes[id(linked_cond)]]
			#replace the variable with the current value the LinkedCond object is being tested as
			lim_variables_to_cond[cond_variable] = linked_cond_value
			#test if limitation is satisfied for current numbers
			if not _testEquation(lim_formula, lim_variables_to_cond, limitation[2], limitation[3]):
				#if it isn't satisfied, set variable to False
				satisfies_linked_cond = False
				break
	if not satisfies_linked_cond:
		break
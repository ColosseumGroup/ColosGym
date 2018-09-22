result = open('/home/goodman/POKER/project_acpc_server_v1.0.41/project_acpc_server/matchName.log','r')
Total_reward = 0.0
playerName = 'Alice'
while True:
	state_str = result.readline().rstrip('\n')
	if len(state_str)<2:
		break
	state_list = state_str.split(":")
	if len(state_list)==6:
		reward_dict = dict(zip(state_list[5].split('|'),state_list[4].split('|')))
		reward = float(reward_dict[playerName])
		Total_reward += reward
print(Total_reward)
#not using anymore

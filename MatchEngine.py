#rates = {CCYpair_1: rate_1, CCYpair_2: rate_2,...}
#CCYAm = {CCYpair_1: [ccy1_Am,ccy2_Am], CCYpair_2: [ccy1_Am,ccy2_Am],...}
def clearing(rates,CcyAm):
	CcyRe = {}
	for CCY in CcyAm:
		if CcyAm[CCY][0] != 0 and CcyAm[CCY][1] != 0:
			cnvAm = CcyAm[CCY][0]*rates[CCY] #change CCY1 into equivalent CCY2
			if cnvAm <= CcyAm[CCY][1]: #to convert all CCY1 to CCY2, CCY2 might have some left over
				#put money to Return Account:
				CcyRe[CCY]=[CcyAm[CCY][0],cnvAm]
				#clear money in Currency Account:
				CcyAm[CCY][0] = 0
				CcyAm[CCY][1] -= cnvAm
			else: #to convert all CCY2 to CCY1, CCY1 should have some left over
				cnvAm = CcyAm[CCY][1]*(1.0/rates[CCY])
				CcyRe[CCY] = [cnvAm,CcyAm[CCY][1]]
				CcyAm[CCY][0] -= cnvAm
				CcyAm[CCY][1] = 0
	return CcyRe

#input: total: money needs to be distributed, listOfCust: list of persons to be distributed money
#output: the list of Customers together with their distributed money
#total = 0 after the process
#do not allowed total > money need to be distributed
def distribute_Money(total, listOfCust):
	dealt_list = []
	while total > 0 :
		#deal with the first customer in the list
		customer = listOfCust[0]
		if customer[1] >= total:
			customer[1] -= total
			dealt_list.append([customer[0],round(total,2)])
			total = 0
		else:
			total -= customer[1]
			dealt_list.append([customer[0],round(customer[1],2)])
			customer[1] = 0
		#remove customer that has settled request
		if customer[1] == 0:
			listOfCust.pop(0)
	return dealt_list

#CustReq = {CCYpair_1: [ [ [Cust1, Am1],...], [ [Cust2, Am2],...] ], CCYpair_2:...}
#the first list in each element of the dictionary is for the Customers who placed CCY2 and want the CCY1, and vice versa for the 2nd list
def requestSettle(CustReq,ReAm):
	reqClear = {}
	for CCY in ReAm:
		reqClear[CCY] = []
		for i in range(0,2):
			amount = ReAm[CCY][i]
			cust_list = CustReq[CCY][i]
			reqClear[CCY].append(distribute_Money(amount, cust_list))
		#clear for the 1st CCY in the pair
	return reqClear

#turning Customer Request to clearing account/ match and return
def postOrder(request,rates,matchAcc):
	for CCY in request:
		total1 = 0
		total2 = 0
		# one for CCY1, one for CCY2
		for each in request[CCY][0]:
			total1 += each[1]
		for each in request[CCY][1]:
			total2 += each[1]
		if CCY in matchAcc:
			matchAcc[CCY][0] = total1
			matchAcc[CCY][1] = total2
		else:
			matchAcc[CCY] = [total1,total2]
	return matchAcc

#position denotes the CCY1/CCY2 that the customer wants to exchange for.
#therefore, the amount unit is the CCY2/CCY1 that customer currently has. (in the opposite of the position CCY)
def add_request(CustID, CCYpair, amount, position, request,rates):
	if CCYpair not in request:
		if position == 1:
			amount *= 1.0/rates[CCYpair]
			request[CCYpair] = [[[CustID, amount]],[]]
		else:
			amount *= rates[CCYpair]
			request[CCYpair] = [[],[[CustID, amount]]]
	else:
		if position == 1:
			amount *= 1.0/rates[CCYpair]
		else:
			amount *= rates[CCYpair]
		request[CCYpair][position-1].append([CustID, amount])
	return

rates = {'USDSGD': 1.2658, 'USDMYR': 3.2270}
request = {}
add_request('Alan', 'USDSGD', 10, 1, request, rates)
add_request('Betty', 'USDSGD', 5, 1, request, rates)
add_request('Alex', 'USDSGD',5, 2, request, rates)
add_request('Bob', 'USDSGD', 17, 2, request, rates)

add_request('Cindy', 'USDMYR', 100, 1, request, rates)
add_request('Dave', 'USDMYR', 76, 1, request, rates)
add_request('Celine', 'USDMYR', 1, 2, request, rates)
add_request('Don', 'USDMYR', 100, 2, request, rates)
matchAcc = {}
#request = {'USDSGD': [ [ ['Alan', 2] ,['Ben', 0.5] ,['Cindy', 5] ], [ ['Alex', 4], ['Bob', 3] ] ]}
matchAcc = postOrder(request,rates,matchAcc)
ccyRe = clearing(rates, matchAcc)
print requestSettle(request,ccyRe)
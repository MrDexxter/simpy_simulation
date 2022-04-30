import simpy
import random

def gp_patient_generator(env, p_interval, mean_registration, mean_gp_consult, mean_test_book, receptionists, gps):
	
	p_id = 0
	while True:
		activity = activity_generator_gp(env, mean_registration, mean_gp_consult, mean_test_book, receptionists, gps, p_id)
		env.process(activity)
		
		next_patiend = random.expovariate(1/p_interval)
		yield env.timeout(next_patiend)
		p_id += 1

def activity_generator_gp(env, mean_registration, mean_gp_consult, mean_test_book, receptionists, gps, p_id):
	global register_queue
	global book_test_queu
	global consultation_queue
	enter_queue_for_register = env.now
	with receptionists.request() as req:
		yield req
		left_queue_for_register = env.now
		time_to_register = left_queue_for_register - enter_queue_for_register
		print("Patient", p_id, "queued for registration for", time_to_register, "minutes.")
		register_queue.append(time_to_register)
		time_to_register = random.expovariate(1/mean_registration)
		yield env.timeout(time_to_register)
	
	enter_queue_for_gp = env.now
	with gps.request() as reqgp:
		yield reqgp
		left_queue_for_gp = env.now
		time_to_gp = left_queue_for_gp - enter_queue_for_gp
		consultation_queue.append(time_to_gp)
		print("Patient", p_id, "queued for gp for", time_to_gp, "minutes.")
		time_to_consult = random.expovariate(1/mean_gp_consult)
		yield env.timeout(time_to_consult)
	
	consult_result = random.uniform(0, 1)
	if consult_result < 0.25:
		enter_queue_for_test_book = env.now
		with receptionists.request() as req:
			yield req
			left_queue_for_test_book = env.now
			time_to_book_test = left_queue_for_test_book - enter_queue_for_test_book
			book_test_queu.append(time_to_book_test)
			print("Patient", p_id, "queued for booking test for", time_to_book_test, "minutes.")
			
			time_to_book_test = random.expovariate(1/mean_test_book)
			yield env.timeout(time_to_book_test)


env = simpy.Environment()
rcpts = simpy.Resource(env, capacity=1)
gps = simpy.Resource(env, capacity=5)
mean_register = 2
mean_gp_consult = 8
mean_book_test = 3
interval = 3
register_queue = []
consultation_queue = []
book_test_queu = []
p = gp_patient_generator(env, interval, mean_register, mean_gp_consult, mean_book_test, rcpts, gps)
env.process(p)
env.run(until=4800)


print("Mean Time To Register", sum(register_queue)/ len(register_queue))
print("Mean Time To Consult", sum(consultation_queue)/len(consultation_queue))
print("Mean Time to Book a Test", sum(book_test_queu)/ len(book_test_queu))
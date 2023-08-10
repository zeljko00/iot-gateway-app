import time
import random
import numpy
from multiprocessing import Process

# period = measuring period in sec, min_val/max_val = min/max measured value
def measure_periodically(period,min_val,max_val):
    # prevent division by zero
    if period==0:
        period=1
    period=abs(round(period))
    # provide sensor with data for 7 days
    values_count=round(7*24*60*60/period)
    data=numpy.random.uniform(min_val,max_val,values_count)
    counter=0
    # shut down sensor?
    while True:
        time.sleep(period)
        # send data to iot gateway
        print(data[counter%values_count])
        counter+=1

# min_t/max_t = min/max measuring period in sec, min_val/max_val = min/max measured value
def measure_randomly(min_t, max_t, min_val,max_val):
    # parameter validation
    if max_t<=min_t:
        max_t=min_t+random.randint(10)
    min_t=abs(round(min_t))
    max_t=abs(round(max_t))
    # provide sensor with data for at least 7 days
    values_count = round(7 * 24 * 60 * 60 / min_t)
    intervals=numpy.random.uniform(min_t,max_t,values_count)
    data = numpy.random.uniform(min_val, max_val, values_count)
    counter = 0
    # shut down sensor?
    while True:
        time.sleep(round(intervals[counter%values_count]))
        # send data to iot gateway
        print(data[counter%values_count])
        counter += 1

# period = measuring interval , capacity = fuel tank capacity , refill = fuel tank refill probability (0-1)
# consumption = fuel usage consumption per working hour, efficiency = machine work efficiency (0-1)
def measure_fuel_periodically(period, capacity, consumption, efficiency, refill):
    # parameter validation
    if period==0:
        period=1
    period=abs(round(period))

    # at first fuel tank is full
    value=random.randint(round(capacity/2),round(capacity))
    # constant for scaling consumption per hour to per second
    scale=1/(60*60)
    # shut down sensor?
    refilling = False
    while True:
        time.sleep(period)

        # fuel tank is filling
        if(refilling):
            value=capacity
            refilling=False
        else:
            # deciding whether fuel tank should be refilled based on refill probability
            refilling = random.random() < refill
            # amount of consumed fuel is determined based on fuel consumption, time elapsed
            # from previous mesuring and machine state (on/of)
            consumed=period*consumption*scale*(1+1-efficiency)
            value-=consumed;
            if value<=0:
                value=0
                refilling=True
        # send data to iot gateway
        print(value)


temperature_sensor = Process(target=measure_periodically, args=(2, 10, 100))
excavator_arm_sensor = Process(target=measure_randomly, args=(1, 4, 0, 800))
fuel_sensor = Process(target=measure_fuel_periodically, args=(7, 295, 3000, 0.6, 0.01))
def main():
    # temperature_sensor.start()
    # excavator_arm_sensor.start()
    fuel_sensor.start()

if __name__ == '__main__':
    main()




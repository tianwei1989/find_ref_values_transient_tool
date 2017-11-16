"""
BRIEF: SOLVE THE EQUATIONS TO FIND REFERENCE VALUES FOR EFFICACY AND COLD STREAM FLOW RATES USING
        GENETIC ALGORITHM
AUTHOR: WEI TIAN, CHRIS HEALEY
DATE: 11/16/2017
"""
## NOTE THAT pyeasyga IS OBTAINED FROM https://github.com/remiomosowon/pyeasyga
## UNDER BSD 3-CLAUSE NEW OR REVISED LICENSE
import pyeasyga

class find_ref (object):
    """
    DEFINE INPUT PARAMETERS AND VARIABLES
    """
    def __init__(self):
        #Known
        self.q_it = 30000.0 #IT load 30 kW
        self.q_max = 75000.0 #Chiller nominal capacity 75 kW
        self.C_h_ref = 4000.0 #Reference for hot stream capacity
        self.deltaT_ch = 2.0 #Temperature difference at chiller 2 degC
        self.c_p_w = 4217.0 #Specific heat capacity of water
        self.c_p_a = 1005.0 #Specific heat capacity of air
        self.T_s_a = 16.0 #Temperature of supply air to the room
        self.T_stor = 15.0 #Temperature of water in the tank
        self.C_h = self.C_h_ref #Heat capacity of air
        self.C_ch = self.q_it/self.deltaT_ch #Heat capacity of chilled water
        self.C_cc = self.C_ch*(self.q_it/self.q_max) #Heat capacity of cooling coil water
        self.T_r_a = self.T_s_a + self.q_it/self.C_h_ref #Temperature of returned air from room
        #Find
        self.effi1_Cch_Ch = 0.75 #Efficacy 1 
        self.effi2_Ccc_Ch = 0.75 #Efficacy 2
        self.C_c_ref = self.C_ch #Reference heat capacity of Cc_Ref
        self.effi_ref = 0.75 #Reference efficacy

    """
    CALCULATE THE EFFICACY 1
    """
    def getEffi1(self):
        return (self.q_max/(min(self.C_ch,self.C_h)*(self.T_s_a+self.q_max/self.C_h-self.T_stor)))

    """
    CALCULATE THE EFFICACY 2
    """
    def getEffi2(self):
        return (self.q_it/(min(self.C_cc,self.C_h)*(self.T_s_a+self.q_it/self.C_h-self.T_stor)))

    """
    GIVEN TWO EQUATIONS WITH TWO UNKNOWNS, FIND C_c_ref AND effi_ref
        :C_c: SPECIFIED BY THE USER, EITHER C_ch OR C_cc
        :TREAT THE EQUATION SOLVING AS AN OPTIMIZATION PROBLEM
        :TRY GENETIC ALGORITHM
    """
    def getEffiEpsilon(self, C_c):
        ## Parameter
        efficacy=0.0
        Effi_ref = self.effi_ref
        C_h = self.C_h
        C_c_ref = self.C_c_ref
        C_h_ref = self.C_h_ref
        C_min = min (C_c, C_h)
        C_max = max (C_c, C_h)
        C_ref_min = min (C_c_ref,C_h_ref)
        C_ref_max = max (C_c_ref,C_h_ref)

        ## Caclulate alpha and efficacy
        alpha = (2*pow(C_c/C_c_ref,0.8)*pow(C_h/C_h_ref,0.8)*C_ref_min*(1-C_min/C_max))/((pow(C_c/C_c_ref,0.8)+pow(C_h/C_h_ref,0.8))*C_min*(1-C_ref_min/C_ref_max))
        efficacy = 1-(1-C_min/C_max)/(pow((1-Effi_ref*(C_ref_min/C_ref_max))/(1-Effi_ref),alpha)-C_min/C_max)
        return (efficacy)
"""
DEFINE FITNESS FUNCTION FOR GA
"""
def fitness(individual, data):
    #instantiate the find efficacy model
    effi_ins=find_ref()
    C_ch = effi_ins.C_ch
    C_cc = effi_ins.C_cc
    #assign values to the unknowns
    effi_ins.effi_ref = individual[0]
    effi_ins.C_c_ref = individual[1]
    print (effi_ins.effi_ref,effi_ins.C_c_ref)
    #Caculate the error
    Effi1_LHS = effi_ins.getEffiEpsilon(C_ch)
    Effi2_LHS = effi_ins.getEffiEpsilon(C_cc)
    Effi1_RHS = effi_ins.getEffi1()
    Effi2_RHS = effi_ins.getEffi2()
    error = 0.5*(abs(Effi1_RHS-Effi1_LHS) + abs(Effi2_RHS-Effi2_LHS))
    print ("--------------->"+str(1/error))
    #return
    return (1/error)
"""
CREATE THE SEEDS
"""
def create_individual(data):
    import random
    individual=[random.uniform(0.01,0.99),random.uniform(10,10000)]
    print (individual)
    return (individual)
"""
DEFINE THE MUTATE (GENE CHANGE)
"""
def mutate(individual):
    import random
    """Reverse the bit of a random index in an individual."""
    mutate_index = random.randrange(len(individual))
    individual[mutate_index] = (random.uniform(0.1,0.9), random.uniform(10,10000))[individual[mutate_index] == 0]

"""
ENTRANCE OF THE PROGRAM
"""      
if __name__ == "__main__":
    ## Call GA to solve the equation
    data=[{"effi_ref"},{"C_c_ref"}]
    ga = pyeasyga.GeneticAlgorithm(data, population_size=10,
                 generations=20,mutation_probability=0.2,crossover_probability=0.9)
    ga.create_individual = create_individual
    ga.mutate_function = mutate
    ga.fitness_function = fitness               # set the GA's fitness function
    ga.run()
    # Print results
    print (ga.best_individual())                  # print the GA's best solution
    

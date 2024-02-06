import FirstOrderCalcs as FAC

def add_intro(file_name):
    '''Adds the introduction to the document with file_name'''
    file = open(file_name, 'w')

    file.write("##########################################"+'\n')
    file.write("\n")
    file.write("Analysis by the Society for Advanced Rocket Propulsion"+"\n")
    file.write("At the University of Washington"+"\n")
    file.write("\n")
    file.write("##########################################")

    file.close()

    print("Intro Printed")

    return


def print_FAC_inputs(file_name, params):
    
    ''''Takes in the given params and then outputs the input parameters
    into the file with name "file name"
    if they exist and skips them if they do not exist'''

    # This first part takes the current file 

    file = open(file_name, 'a')
    
    file.write("###########################################"+"\n")
    file.write("\n")
    file.write("These are the inputs taken by our first order calculations:"+"\n"+"\n")

    print(params)

    '''for index in params:
        if not params[index] is None:
            file.write(str(index)+": "+str(params[index]))'''

    file.close()


x = add_intro("./Analysis/FAC_Output.txt")

'''y = print_FAC_inputs("./Analysis/FAC_Output.txt", None)'''


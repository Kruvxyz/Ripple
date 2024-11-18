from Routine import Routine

def gen_building_graph_routine() -> Routine:
    def building_graph_function() -> bool:
        print("Building Graph")
        # organize new data
        # ------------------
        # flag data that needs to be added into the graph
        #  
        # 
        # turn data into vector
        # push to vector_db
        # find nearest neighbors
        # use LLM to map the associations
        # push the associations to the db (node + edges)
        # mark the data as processed
        # 
        # 

        return True
    
    return Routine(
        "Building_Graph",
        "This routine builds the graph.",
        building_graph_function,
        1 # 1 minute
    )
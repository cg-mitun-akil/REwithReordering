import sys
sys.path.append("..")
import os
import json
import time
import random
import numpy as np
from collections import deque

output_folder = "../output"
folder_path = "../benchmarks"

class node( object ):

    def __init__( self , name , level , lastAccepted = -1 ):
        self.name = name 
        self.level = level
        self.children = dict()
        self.parent = set()
        self.lastAccepted = lastAccepted

    def show( self ):
        print("Node details")
        print( self.name , self.level , self.lastAccepted )
        for par in self.parent:
            print("****", par.name , par.level , par.lastAccepted )
        for ch in self.children:
            print( "%%%%%", ch , self.children[ch].name , self.children[ch].level  , self.children[ch].lastAccepted )

class EnforcerBuffer( object ):

    def __init__( self , alphabet , mappings , startState , acceptedStates ):
        self.alphabet = alphabet
        self.KingState = node( 'K' , -1 )
        self.KingState.children['a'] = node( startState , 0 )
        (self.KingState.children['a']).parent = { self.KingState }
        self.lastLevel = [ (self.KingState.children)['a'] ]
        self.mappings = mappings
        self.buffer = list()
        self.expected = 0
        self.baseIndex = 0
        self.level = dict()
        self.size = 2
        self.acceptedStates = acceptedStates
        self.reserve = list()
        self.baseReserveIndex = 0

    def insert( self , event ):
        if( event is None or event[0] is None ):
            return []
        
        if self.expected == event[1]:
            self.buffer.append( event[0] )
            nx = dict()
            lv = list()
            for state in self.lastLevel:
                st = self.mappings[ state.name ][ event[0] ]
                val = state.lastAccepted
                #print( state.name , event[0] , event[1] , st , val , "--" )
                if st in self.acceptedStates:
                    val = self.expected
                if (st,val) not in nx:
                    nx[( st , val )] = node( st , self.expected , val  )
                    self.size = self.size + 1
                    lv.append( nx[( st , val )] )
                for par in state.parent:
                    for ch in par.children:
                        if par.children[ch] == state:
                            par.children[ch] = nx[( st , val )]
                            nx[( st , val )].parent.add( par )
                self.size = self.size - 1
            self.lastLevel = lv
            self.expected = self.expected + 1
        
        output = []
        if (self.KingState.children['a']).lastAccepted >= self.baseIndex:
            output = self.buffer[: (self.KingState.children['a']).lastAccepted - self.baseIndex + 1 ]
            self.buffer = self.buffer[ (self.KingState.children['a']).lastAccepted - self.baseIndex + 1 : ]
            self.baseIndex += len( output )

        return output 
    
    def send( self , event ):
        if( event is None or event[0] is None ):
            return []
        output = list()
        if len( self.reserve ) > 0:
            if event[1] < self.baseReserveIndex:
                output.extend( self.insert( event ) )
            elif event[1] < self.baseReserveIndex + len( self.reserve ):
                self.reserve[ event[1] - self.baseReserveIndex ] = event 
            else:
                self.reserve += [None for _ in range(event[1] - len(self.reserve) - self.baseReserveIndex)]
                self.reserve.append(event)
        elif self.expected == event[1]:
            output.extend( self.insert( event ) )
        else:
            self.baseReserveIndex = self.expected + 1
            self.reserve = list()
            self.reserve += [None for _ in range(event[1] - len(self.reserve) - self.baseReserveIndex )]
            self.reserve.append(event)
            #print("----",event, self.reserve)

        if len( self.reserve ) > 0:
            while len( self.reserve ) > 0 and self.reserve[0] != None and self.reserve[0][0] != None and self.reserve[0][1] == self.expected:
                output.extend( self.insert( self.reserve[0] ) )
                del self.reserve[0]
                #print(' adding to tree ')
                self.baseReserveIndex = self.baseReserveIndex + 1
        #print( event , output, self.reserve )
        return output

class EnforcerHybrid( object ):

    def __init__( self , alphabet , mappings , startState , acceptedStates , alpha , beta ):
        self.alphabet = alphabet
        self.KingState = node( 'K' , -1 )
        self.KingState.children['a'] = node( startState , 0 )
        (self.KingState.children['a']).parent = { self.KingState }
        self.lastLevel = [ (self.KingState.children)['a'] ]
        self.mappings = mappings
        self.buffer = list()
        self.expected = 1
        self.baseIndex = 0
        self.level = dict()
        self.size = 2
        self.acceptedStates = acceptedStates
        self.reserve = list()
        self.baseReserveIndex = 0
        self.alpha = alpha
        self.beta = beta

    def draw( self ):
        print("######################################")
        self.KingState.show()
        print("---------------------------")
        for leve in self.level:
            print(leve)
            for node in self.level[leve]:
                node.show()
                print('.................................')
            print('---------------------------')
        print("LAST LEVEL" , len( self.lastLevel) )
        for node in self.lastLevel:
            node.show()
            print('.................................')
        print("######################################")

    def clean( self , levelID ):
        newList = list()
        for state in self.level[levelID]:
            if state.parent is None or ( len( state.parent ) == 0 ):
                if state.children != None:
                    for ch in state.children:
                        if state in (state.children[ch]).parent:
                            (state.children[ch]).parent.remove( state )
                self.size = self.size - 1
            else:
                newList.append( state )
        self.level[levelID] = newList  

    def lastClean( self ):
        newList = list()
        for state in self.lastLevel:
            if state.parent is None or ( len( state.parent ) == 0 ):
                if state.children != None:
                    for ch in state.children:
                        if state in (state.children[ch]).parent:
                            (state.children[ch]).parent.remove( state )
                self.size = self.size - 1
            else:
                newList.append( state )
        self.lastLevel = newList 

    def purge( self , cleanLevel ):
        if cleanLevel != None:
            for lev in sorted( self.level.keys() ):
                if lev >= cleanLevel:
                    self.clean( lev )
        self.lastClean()

    def branch( self ):
        self.level[ self.expected ] = self.lastLevel
        lv = list()
        self.buffer.append(None)
        nx = dict()
        for state in self.lastLevel:
            for alph in self.alphabet:
                st = self.mappings[ state.name ][ alph ]
                val = state.lastAccepted
                if st in self.acceptedStates:
                    val = self.expected
                if (st,val) not in nx:
                    nx[( st , val )] = node( st , self.expected , val  )
                    self.size = self.size + 1
                    lv.append( nx[( st , val )] )
                state.children[ alph ] = nx[( st , val )]
                nx[( st , val )].parent.add(state)
        self.lastLevel = lv 
        self.expected = self.expected + 1

    def insert( self , event ):
        if( event is None or event[0] is None ):
            return []
        while ( self.expected < event[1] ):
            self.branch()
        
        if self.expected == event[1]:
            self.buffer.append( event[0] )
            nx = dict()
            lv = list()
            for state in self.lastLevel:
                st = self.mappings[ state.name ][ event[0] ]
                val = state.lastAccepted
                #print( state.name , event[0] , event[1] , st , val , "--" )
                if st in self.acceptedStates:
                    val = self.expected
                if (st,val) not in nx:
                    nx[( st , val )] = node( st , self.expected , val  )
                    self.size = self.size + 1
                    lv.append( nx[( st , val )] )
                for par in state.parent:
                    for ch in par.children:
                        if par.children[ch] == state:
                            par.children[ch] = nx[( st , val )]
                            nx[( st , val )].parent.add( par )
                self.size = self.size - 1
            self.lastLevel = lv
            self.expected = self.expected + 1

        elif self.expected > event[1]:
            self.buffer[ event[1] - 1 - self.baseIndex ] = event[0]
            cleanLevel = None
            for state in self.level[ event[1] ]:
                for alph in self.alphabet:
                    if alph in state.children and alph != event[0]:
                        if state in (state.children[alph]).parent:
                            (state.children[alph]).parent.remove( state )
                            cleanLevel = event[1] + 1
                    elif alph in state.children and alph == event[0]:
                        for par in state.parent:
                            for ch in par.children:
                                if par.children[ch] == state:
                                    par.children[ch] = state.children[ event[0] ]
                                    (state.children[ event[0] ]).parent.add(par)
            #print('&&&&&&&&&&&&&&&&&&&&&&&&&')
            #print( self.size , cleanLevel , self.KingState.children['a'].name )
            #print( self.level.keys() , len( self.lastLevel) )
            #self.draw()
            self.purge( cleanLevel )
            #print( self.size , len(self.lastLevel) )
            #self.draw()
            #print( self.size , self.expected , cleanLevel , event[1] , len( self.level[ event[1] ]))
            self.size = self.size - len( self.level[ event[1]] )
            del self.level[ event[1] ]
            #print( self.size , cleanLevel , event[1] )
        output = []
        if (self.KingState.children['a']).lastAccepted - 1 >= self.baseIndex:
            output = self.buffer[: (self.KingState.children['a']).lastAccepted - 1 - self.baseIndex + 1 ]
            self.buffer = self.buffer[ (self.KingState.children['a']).lastAccepted - 1 - self.baseIndex + 1 : ]
            self.baseIndex += len( output )

        return output 
    
    def send( self , event ):
        if( event is None or event[0] is None ):
            return []
        output = list()
        if len( self.reserve ) > 0:
            if event[1] < self.baseReserveIndex:
                output.extend( self.insert( event ) )
            elif event[1] < self.baseReserveIndex + len( self.reserve ):
                self.reserve[ event[1] - self.baseReserveIndex ] = event 
            else:
                self.reserve += [None for _ in range(event[1] - len(self.reserve) - self.baseReserveIndex)]
                self.reserve.append(event)
        else:
            while self.expected < event[1] and self.size < self.beta:
                self.branch()
            if event[1] <= self.expected:
                output.extend( self.insert( event ) )
            else:                                     # program comes here only if we could not branch
                #print('creating reserve' , event , self.expected , self.size )
                self.baseReserveIndex = self.expected + 1
                self.reserve = list()
                self.reserve += [None for _ in range(event[1] - len(self.reserve) - self.baseReserveIndex )]
                self.reserve.append(event)

        if len( self.reserve ) > 0 and self.size <= self.alpha:

            while self.size < self.beta and len( self.reserve ) > 0 and self.reserve[0] != None and self.reserve[0][0] != None:
                output.extend( self.insert( self.reserve[0] ) )
                del self.reserve[0]
                #print(' adding to tree ')
                self.baseReserveIndex = self.baseReserveIndex + 1
        return output

def remove_and_append(lst, x):
    num_elements_to_remove = min( max( int(len(lst) * x) , 4 ) , len(lst) )
    removed_elements = random.sample(lst, num_elements_to_remove)
    for elem in removed_elements:
        lst.remove(elem)
    lst.extend(removed_elements)
    return lst

def reorder( lst , x , batch_size ):
    res = list()
    batch_size = max( 1 , batch_size )
    for i in range(0, len(lst), batch_size):
        batch = lst[i:i+batch_size]
        res.extend( remove_and_append(batch,x) )
    return res
      
def processData( data , filename , prob , events ):
    print(filename)
    M = EnforcerHybrid( data['alphabets'] , data['mp'] , data['startState'] , data['acceptedStates'] , 700 , 1000  )
    outputH = []
    res = dict()
    memoryMonitorH = list()
    index = 1
    print("hybrid start")
    mx = 2
    res['startTimeH'] = time.time()
    for event in events:
        outputH = outputH + [M.send( ( event[0] , event[1] + 1 ))]
        memoryMonitorH.append( [ M.size , index ] )
        mx = max( M.size , mx )
        index = index + 1
    res['endTimeH'] = time.time()
    memoryMonitorH.append( [ 2 , index ] )
    res['durationH'] = res['endTimeH'] - res['startTimeH']
    print("hybrid end", res['durationH'] )
    return [res['durationH'] , mx ]          

def plotMemVSize( data , filename ):
    print(filename)
    M = EnforcerHybrid( data['alphabets'] , data['mp'] , data['startState'] , data['acceptedStates'] , 50 , 100  )
    N = EnforcerBuffer( data['alphabets'] , data['mp'] , data['startState'] , data['acceptedStates'] )
    outputH = []
    events = data['events']
    events = reorder( events , 0.01 , 1000 )
    events = reorder( events , 0.0005 , 30000 ) 
    res = dict()
    memoryMonitorH = list()
    index = 1
    print("hybrid start")
    mx = 2
    res['startTimeH'] = time.time()
    for event in events:
        outputH = outputH + [M.send( ( event[0] , event[1] + 1 ))]
        memoryMonitorH.append( [ M.size , index ] )
        mx = max( M.size , mx )
        index = index + 1
    res['endTimeH'] = time.time()
    memoryMonitorH.append( [ 2 , index ] )
    res['durationH'] = res['endTimeH'] - res['startTimeH']
    print("hybrid end", res['durationH'] )
    outputB = []
    print("buffer start")
    index = 1
    memoryMonitorB = list()
    res['startTimeB'] = time.time()
    for event in events:
        outputB = outputB + [N.send(event)]
        memoryMonitorB.append( [ N.size , index ] )
        index = index + 1
    res['endTimeB'] = time.time()
    res['durationB'] = res['endTimeB'] - res['startTimeB'] 
    print("buffer end" , res['durationB'] )
    res['outputH'] = outputH
    res['memoryMonitorH'] = memoryMonitorH
    res['outputB'] = outputB
    res['memoryMonitorB'] = memoryMonitorB

    output_filename = os.path.splitext(filename)[0] + '_output.json'
    with open(os.path.join(output_folder, output_filename), 'w') as output_file:
        json.dump( res , output_file)

def plotTimVProb( output_folder , folder_path , filename ):
    start_prob = 0.0005
    end_prob = 0.0017
    num_iterations = 2

    step = (end_prob - start_prob) / num_iterations
    results = {}
    damon = {}
    file_path = os.path.join(folder_path, filename)
    with open(file_path, 'r') as file:
        data = json.load(file)
    for i in range(num_iterations+1):
        probability = start_prob + i * step
        values = []
        kuv = []
        print(i)
        for _ in range(6):
            events = data['events']
            events = reorder( events , probability , 20000 )
            result = processData( data , filename , probability , events )
            values.append(result[0])
            kuv.append(result[1])
            print(result)
        avg_value = sum(values) / len(values)
        results[probability] = avg_value
        avg_value = sum(kuv) / len(kuv)
        damon[probability] = avg_value

    with open(os.path.join(output_folder,   'tim_res' + filename) , 'w') as json_file:
        json.dump(results, json_file, indent=4)
    with open(os.path.join(output_folder,   'mem_res' + filename) , 'w') as json_file:
        json.dump(damon, json_file, indent=4)

    print("Results saved")

def runBenchmark( output_folder , folder_path ):
    for filename in os.listdir(folder_path):
        if filename.endswith('.json') and filename.startswith('test_'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r') as file:
                data = json.load(file)
            plotMemVSize( data , filename )

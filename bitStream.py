import math
import operator
import copy
    
class BitIterator:
    # Iterates over the bits starting from the smallest bit
    def __init__(self, stream, length):
        self.stream = int(stream)
        self.length = int(length)
        
    def __iter__(self):
        return self
    
    def __reversed__(self):
        reversedStream = sum(1<<(self.length-1-i) for i in range(self.length) if self.stream>>i&1)
        return BitIterator(reversedStream, self.length)
    
    def __copy__(self):
        return BitIterator(self.stream, self.length)
    
    def __deepcopy__(self, data = None):
        return BitIterator(self.stream, self.length)    
    
    def next(self):
        if self.length <= 0:
            raise StopIteration
        
        bitValue = self.stream % 2
        self.length -= 1
        self.stream >>= 1

        return int(bitValue)
        
class BitStream:
    def __init__(self, bits = None, length = None):
        self.stream = 0
            
        self.length = 0
        
        self.push(bits, length)

            
    def __str__(self):
        return repr(self)
    
    def __repr__(self):
        return ('{:#0%db}' % (self.length + 2)).format(self.stream)
    
    def __hash__(self):
        return hash((self.length, self.stream))
        
    def __len__(self):
        return self.length
    
    def __int__(self):
        return sum(1<<(self.length-1-i) for i in range(self.length) if self.stream>>i&1)
    
    def __iter__(self):
        return BitIterator(self.stream, self.length)
    
    def __reversed__(self):
        reversedStream = sum(1<<(self.length-1-i) for i in range(self.length) if self.stream>>i&1)
        return BitIterator(reversedStream, self.length)
    
    def __add__(self, other):
        clone = copy.copy(self)
        clone += other
        return clone
    
    def __iadd__(self, other):
        self.push(other)
        return self
    
    def __eq__(self, other):
        return self.stream == other.stream
    
    def __copy__(self):
        clone = BitStream()
        clone.stream = self.stream
        clone.length = self.length
        return clone
    
    def __deepcopy__(self, data = None):
        return BitStream(self.stream, self.length)
    
    def reverse(self):
        self.stream = sum(1<<(self.length-1-i) for i in range(self.length) if self.stream>>i&1)
        return self
        
    def pop(self):
        '''
        Removes and returns a bit from the beginning (right) of the stream
        '''
        
        if self.length <= 0:
            raise IndexError('pop from empty Bitstream')
        
        self.length -= 1
        bitValue = self.stream % 2
        self.stream >>= 1
        
        return int(bitValue)
        
    def pushBit(self, bit):    
        '''
        Adds a bit to the end (left) of the stream
        '''
        
        if bit:
            self.stream += (1 << self.length)
            
        self.length += 1
            
    def push(self, bits, length = None):
        '''
        Adds bits to the end of the stream
        @param bits - The data to push onto the stream
        @param length - The number of bits to push onto the stream
        
        Default length is:
            char   - 8
            number - The least number of bits
        '''
        
        try:
            # Assume input ia a char
            # Try to cast to int
            bits = ord(bits)
            
            # Default length for char is 8 bits
            if length is None:
                length = 8
        except TypeError:    
            pass
    
        try:
            # Check to see if we have a lenght e.g. bits is a BitStream
            if length is None:
                try:
                    length = len(bits)
                except TypeError:
                    pass
            
            # Assume the input is a number
            bits = int(bits)
            
            if length is None:
                try:
                    # The default length is the least number of bits to store the number
                    length = math.floor(math.log(bits,2)) + 1   
                except ValueError:
                    length = 1
                
            # If bits equals zero, then we can just increase the length
            if bits == 0:
                self.length += length
            else:
                # Otherwise push the bits onto the stream
                for b in reversed(BitIterator(bits, length)):
                    self.pushBit(b)
        except (TypeError, ValueError, AttributeError):    
            pass        
    
        try:
            streams = []
            for i in bits:
                streams.append(BitStream(i))
            addedLen = 0
            for s in streams:
                addedLen += len(s)
                for b in s:
                    self.pushBit(b)
            self.length += length - addedLen
        except TypeError:
            pass        
            
    def next(self):
        try:
            return self.pop()
        except IndexError:
            raise StopIteration
        
        
def opBitStream(op, bs1, bs2 = None):
    if bs2 is not None:
        return BitStream(op(bs1.stream, bs2.stream), min(len(bs1), len(bs2))).reverse()
    
    print bs1.stream, op(bs1.stream)
    return BitStream(op(bs1.stream), len(bs1)).reverse()

def xorBitStream(bs1, bs2):
    return opBitStream(operator.xor, bs1, bs2)

def andBitStream(bs1, bs2):
    return opBitStream(operator.and_, bs1, bs2)

def orBitStream(bs1, bs2):
    return opBitStream(operator.or_, bs1, bs2)

def notBitStream(bs1):
    return opBitStream(lambda x: operator.neg(x)-1, bs1)
    
if __name__ == '__main__':
    bits = BitStream(0b110110)
    print bits
    
    bits2 = BitStream('a')
    print bits2
    for b in bits:
        print b,
        bits2.push(b)
    print
    print bits2
    
    bits.push(500)
    bits2.push(0)
    print bits
    
    bits3 = BitStream()
    for a, b in zip(bits, bits2):
        print a != b,
        bits3.push(a != b)    
    
    print '\n',bits3
    print BitStream(bits.stream ^ bits2.stream, min(len(bits), len(bits2))).reverse()
    print
    print bits
    print bits2
    print andBitStream(bits, bits2)
    print
    print notBitStream(BitStream('\0\0'))
    print
    bits.push(False)
    bits2.push(bits)  
    print bits
    print bits2
    print
    
    bits4 = BitStream('a')
    bits5 = BitStream()
    bits5.push('a')
    print bits4
    print bits5
    print bits4 + bits5
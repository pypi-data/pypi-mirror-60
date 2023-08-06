def sting_to_binary(x):
    t=[]
    for i in x:
        if len(format(ord(i),'b'))==7:
            t.append(format(ord(i),'b'))
        elif len(format(ord(i),'b')) < 7:
            n=8-int(len(format(ord(i),'b')))
            s=''
            while len(s)!=n-1:
                s='0'+s 
    
                t.append(s + format(ord(i),'b'))      
    listToStr = ''.join(map(str, t))      
    return str(listToStr) 







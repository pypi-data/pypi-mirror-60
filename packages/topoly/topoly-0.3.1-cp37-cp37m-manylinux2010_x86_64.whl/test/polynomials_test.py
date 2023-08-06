from topoly import *

# importing the file 31.xyz. It is closed knot.
curve = 'data/31.xyz'

def test_polynomials():
    polynomials = {}
    # calculating the polynomials
    polynomials['Alexander'] = alexander(curve, closure=Closure.CLOSED, poly_reduce=False, translate=True)
    #polynomials['Conway'] = conway(curve, closure=Closure.CLOSED, poly_reduce=False, translate=True)
    polynomials['Jones'] = jones(curve, closure=Closure.CLOSED, poly_reduce=False, translate=True)
    polynomials['HOMFLY-PT'] = homfly(curve, closure=Closure.CLOSED, poly_reduce=False, translate=True)
    #polynomials['Kauffman bracket'] = kauffman_bracket(curve, closure=Closure.CLOSED, poly_reduce=False, translate=True)
    #polynomials['Kauffman polynomial'] = kauffman_polynomial(curve, closure=Closure.CLOSED, poly_reduce=False, translate=True)
    #polynomials['BLM/Ho'] = blmho(curve, closure=Closure.CLOSED, poly_reduce=False, translate=True)
    #polynomials['Yamada'] = yamada(curve, closure=Closure.CLOSED, poly_reduce=False, translate=True)

    # Printing the polynomials and matching knot from the dictionary. We need the short version of the polynomial
    print("Knot polynomials for the 3_1 knot:")
    for key in polynomials.keys():
        #print(key, polynomials[key], find_matching(polynomials[key]))
        print(key, polynomials[key])
        assert polynomials[key].get('3_1')==1.0

test_polynomials()
from jigu.core import Dec


def test_captures_correct_precision():
    A = "138875042105.980753034749566779"
    B = "8447.423744387144096286"
    C = "3913.113789811986907029"
    D = "0.500000000000000000"
    E = "0.006250000000000000"

    assert str(Dec(A)) == A
    assert str(Dec(B)) == B
    assert str(Dec(C)) == C
    assert str(Dec(D)) == D
    assert str(Dec(E)) == E


def test_serializes_zero():
    E = "0.000000000000000000"
    str(Dec(0)) == E


def test_serializes_18_digits():
    A = "0.5"
    B = "0.00625"
    C = "3913.11"

    assert (str(Dec(A))) == "0.500000000000000000"
    assert (str(Dec(B))) == "0.006250000000000000"
    assert (str(Dec(C))) == "3913.110000000000000000"

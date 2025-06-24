"""Basic tests."""

def test_import():
    """Test that package imports."""
    import rd_spiral
    assert rd_spiral.__version__ == "0.1.0"


def test_config():
    """Test config parser."""
    from rd_spiral import parse_config
    
    # Write test config
    with open('test.txt', 'w') as f:
        f.write('d1 = 0.1\n')
        f.write('d2 = 0.1\n')
        f.write('beta = 1.0\n')
        f.write('L = 10.0\n')
        f.write('n = 32\n')
        f.write('t_start = 0.0\n')
        f.write('t_end = 1.0\n')
        f.write('dt = 0.1\n')
    
    config = parse_config('test.txt')
    assert config['d1'] == 0.1
    assert config['n'] == 32
    
    import os
    os.remove('test.txt')

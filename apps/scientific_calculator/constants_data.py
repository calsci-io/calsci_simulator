# Scientific Constants Data
# Format: (symbol, full_name, value_string)
# All values from CODATA 2018/2022 recommended values

SCIENTIFIC_CONSTANTS = [
    # ============================================
    # MATHEMATICAL CONSTANTS (12)
    # ============================================
    ("pi", "pi", "3.141592653589793"),
    ("e", "euler number", "2.718281828459045"),
    ("phi", "golden ratio", "1.618033988749895"),
    ("sqrt2", "square root 2", "1.4142135623730951"),
    ("sqrt3", "square root 3", "1.7320508075688772"),
    ("sqrt5", "square root 5", "2.23606797749979"),
    ("ln2", "natural log 2", "0.6931471805599453"),
    ("ln10", "natural log 10", "2.302585092994046"),
    ("log2e", "log base 2 of e", "1.4426950408889634"),
    ("log10e", "log base 10 of e", "0.4342944819032518"),
    ("gamma", "euler mascheroni", "0.5772156649015329"),
    ("catalan", "catalan constant", "0.915965594177219"),

    # ============================================
    # PHYSICS - UNIVERSAL CONSTANTS (8)
    # ============================================
    ("c", "speed of light", "2.99792458e8"),
    ("G", "gravity const", "6.67430e-11"),
    ("h", "planck const", "6.62607015e-34"),
    ("hbar", "reduced planck", "1.054571817e-34"),
    ("eps0", "permittivity", "8.8541878128e-12"),
    ("mu0", "permeability", "1.25663706212e-6"),
    ("Z0", "impedance vacuum", "376.730313668"),
    ("ke", "coulomb const", "8.9875517923e9"),

    # ============================================
    # PHYSICS - ELECTROMAGNETIC (10)
    # ============================================
    ("qe", "electron charge", "1.602176634e-19"),
    ("phi0", "flux quantum", "2.067833848e-15"),
    ("G0", "conduct quantum", "7.748091729e-5"),
    ("KJ", "josephson const", "4.835978484e14"),
    ("RK", "von klitzing", "25812.80745"),
    ("muB", "bohr magneton", "9.2740100783e-24"),
    ("muN", "nuclear magneton", "5.0507837461e-27"),
    ("ge", "electron g factor", "-2.00231930436256"),
    ("mue", "electron mag mom", "-9.2847647043e-24"),
    ("mup", "proton mag mom", "1.41060679736e-26"),

    # ============================================
    # PHYSICS - ATOMIC & NUCLEAR (15)
    # ============================================
    ("me", "electron mass", "9.1093837015e-31"),
    ("mp", "proton mass", "1.67262192369e-27"),
    ("mn", "neutron mass", "1.67492749804e-27"),
    ("mmu", "muon mass", "1.883531627e-28"),
    ("mtau", "tau mass", "3.16754e-27"),
    ("u", "atomic mass unit", "1.66053906660e-27"),
    ("a0", "bohr radius", "5.29177210903e-11"),
    ("re", "electron radius", "2.8179403262e-15"),
    ("lambdaC", "compton wavelen", "2.42631023867e-12"),
    ("lambdaCp", "proton compton", "1.32140985539e-15"),
    ("lambdaCn", "neutron compton", "1.31959090581e-15"),
    ("Ry", "rydberg const", "1.0973731568160e7"),
    ("Rinf", "rydberg energy", "2.1798723611035e-18"),
    ("Eh", "hartree energy", "4.3597447222071e-18"),
    ("alpha", "fine structure", "7.2973525693e-3"),

    # ============================================
    # PHYSICS - MECHANICS & GRAVITY (5)
    # ============================================
    ("g", "gravity accel", "9.80665"),
    ("gn", "std gravity", "9.80665"),
    ("RE", "earth radius", "6.371e6"),
    ("ME", "earth mass", "5.972e24"),
    ("AU", "astro unit", "1.495978707e11"),

    # ============================================
    # THERMODYNAMICS (8)
    # ============================================
    ("kb", "boltzmann const", "1.380649e-23"),
    ("sigma", "stefan boltzmann", "5.670374419e-8"),
    ("bwien", "wien constant", "2.897771955e-3"),
    ("b2", "wien freq const", "5.878925757e10"),
    ("c1", "1st radiation", "3.741771852e-16"),
    ("c2", "2nd radiation", "1.438776877e-2"),
    ("n0", "loschmidt const", "2.6867774e25"),
    ("Vm0", "molar vol stp", "0.022413969"),

    # ============================================
    # CHEMISTRY (12)
    # ============================================
    ("NA", "avogadro number", "6.02214076e23"),
    ("R", "gas constant", "8.314462618"),
    ("F", "faraday const", "96485.33212"),
    ("Vm", "molar volume", "0.022413969"),
    ("atm", "std atmosphere", "101325"),
    ("bar", "bar pressure", "1e5"),
    ("cal", "calorie", "4.184"),
    ("eV", "electronvolt", "1.602176634e-19"),
    ("kWh", "kilowatt hour", "3.6e6"),
    ("amu", "atomic mass u", "1.66053906660e-27"),
    ("mH", "hydrogen mass", "1.6735575e-27"),
    ("mHe", "helium mass", "6.646477e-27"),

    # ============================================
    # ASTROPHYSICS & COSMOLOGY (10)
    # ============================================
    ("ly", "light year", "9.4607304725808e15"),
    ("pc", "parsec", "3.0856775814914e16"),
    ("MS", "solar mass", "1.98892e30"),
    ("RS", "solar radius", "6.9634e8"),
    ("LS", "solar luminosity", "3.828e26"),
    ("TS", "solar temp", "5778"),
    ("MM", "moon mass", "7.342e22"),
    ("RM", "moon radius", "1.7374e6"),
    ("H0", "hubble const", "2.195e-18"),
    ("tH", "hubble time", "4.55e17"),

    # ============================================
    # NUCLEAR & PARTICLE PHYSICS (12)
    # ============================================
    ("mW", "W boson mass", "1.43297e-25"),
    ("mZ", "Z boson mass", "1.62556e-25"),
    ("mH0", "higgs mass", "2.2295e-25"),
    ("GF", "fermi coupling", "1.1663787e-5"),
    ("sin2W", "weinberg angle", "0.2229"),
    ("alphaS", "strong coupling", "0.1179"),
    ("rp", "proton radius", "8.414e-16"),
    ("sigmae", "thomson cross", "6.6524587321e-29"),
    ("lP", "planck length", "1.616255e-35"),
    ("tP", "planck time", "5.391247e-44"),
    ("mP", "planck mass", "2.176434e-8"),
    ("TP", "planck temp", "1.416784e32"),

    # ============================================
    # UNIT CONVERSIONS (15)
    # ============================================
    ("inch", "inch to meter", "0.0254"),
    ("ft", "foot to meter", "0.3048"),
    ("mile", "mile to meter", "1609.344"),
    ("nmile", "nautical mile", "1852"),
    ("lb", "pound to kg", "0.45359237"),
    ("oz", "ounce to kg", "0.028349523"),
    ("gal", "gallon to liter", "3.785411784"),
    ("degF", "fahrenheit off", "273.15"),
    ("mmHg", "mmhg to pascal", "133.322387415"),
    ("psi", "psi to pascal", "6894.757293168"),
    ("hp", "horsepower", "745.69987158227"),
    ("knot", "knot to m/s", "0.514444444"),
    ("mach", "mach number", "343"),
    ("Btu", "btu to joule", "1055.05585262"),
    ("angstrom", "angstrom", "1e-10"),

    # ============================================
    # CHEMISTRY - ATOMIC WEIGHTS (20)
    # ============================================
    ("ArH", "hydrogen Ar", "1.008"),
    ("ArHe", "helium Ar", "4.0026"),
    ("ArLi", "lithium Ar", "6.94"),
    ("ArC", "carbon Ar", "12.011"),
    ("ArN", "nitrogen Ar", "14.007"),
    ("ArO", "oxygen Ar", "15.999"),
    ("ArF", "fluorine Ar", "18.998"),
    ("ArNe", "neon Ar", "20.180"),
    ("ArNa", "sodium Ar", "22.990"),
    ("ArMg", "magnesium Ar", "24.305"),
    ("ArAl", "aluminum Ar", "26.982"),
    ("ArSi", "silicon Ar", "28.085"),
    ("ArP", "phosphorus Ar", "30.974"),
    ("ArS", "sulfur Ar", "32.06"),
    ("ArCl", "chlorine Ar", "35.45"),
    ("ArAr", "argon Ar", "39.948"),
    ("ArK", "potassium Ar", "39.098"),
    ("ArCa", "calcium Ar", "40.078"),
    ("ArFe", "iron Ar", "55.845"),
    ("ArCu", "copper Ar", "63.546"),

    # ============================================
    # ELECTRONICS & ENGINEERING (8)
    # ============================================
    ("dB", "decibel ratio", "1.1220184543"),
    ("neper", "neper to dB", "8.685889638"),
    ("ohm0", "char impedance", "376.730313668"),
    ("lambda0", "wavelength 1hz", "2.99792458e8"),
    ("f0", "freq 1m wave", "2.99792458e8"),
    ("kT300", "thermal 300K", "4.1419464e-21"),
    ("Vt300", "thermal volt", "0.02585202"),
    ("Iq", "current quantum", "3.874045e-6"),
]


def get_all_constants():
    """Return a copy of all constants."""
    return SCIENTIFIC_CONSTANTS[:]


def search_constants(query):
    """Search constants by symbol or name (case-insensitive)."""
    query = query.lower()
    return [c for c in SCIENTIFIC_CONSTANTS
            if query in c[0].lower() or query in c[1].lower()]

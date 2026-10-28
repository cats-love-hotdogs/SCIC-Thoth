---
name = "math tags"
---
# Description
Allowed tags for JSON files based on `"subject"`. Use **only** tags from this list matching the document's `"subject"` (`"Calculus 1"` or `"Algebra"`). Do not invent new tags.

# Disambiguation Rules

## Calculus 1 Disambiguation
Use mathematical context to distinguish these commonly confused topics:
- Sequence limits (`c1_sequences`) vs. Single-variable function limits (`c1_function_limits`) vs. Multivariable limits (`c3_multivariable_limits`)
- Taylor/Maclaurin for single-variable (`c1_taylor_maclaurin`) vs. multivariable (`c3_higher_order_derivatives`)
- Approximation via single-variable differential (`c1_derivatives_differentials`) vs. Taylor expansion (`c1_taylor_maclaurin`) vs. total differential (`c3_total_differentials`)
- Single-variable extrema (`c1_single_variable_extrema`) vs. unconstrained multivariable extrema (`c3_unconstrained_extrema`) vs. global extrema on closed domain (`c3_global_extrema`)

## Algebra Disambiguation
Use mathematical context to distinguish these commonly confused topics:
- Standard matrix diagonalization (`c4_matrix_diagonalization`) vs. Orthogonal diagonalization of symmetric matrices (`c5_orthogonal_diagonalization`)
- Methods for reducing quadratic forms: Lagrange completion of squares (`c5_lagrange_reduction`) vs. Jacobi method (`c5_jacobi_reduction`) vs. Orthogonal transformation (`c5_orthogonal_reduction_quadratic_form`)
- Eigenvalues and eigenvectors of matrices (`c4_eigenvalues_eigenvectors_matrix`) vs. of linear operators (`c4_eigenvalues_eigenvectors_operator`)
- Matrix rank (`c2_matrix_rank`) vs. Rank of a vector set (`c3_rank_of_vector_set`) vs. Rank / Nullity of a linear mapping (`c4_rank_nullity_theorem`)
- Matrix representation of a linear mapping relative to bases (`c4_matrix_representation`) vs. Change-of-basis transition matrix (`c3_change_of_basis`)
- Solving linear systems via Cramer's rule (`c2_cramer_rule`) vs. Gaussian elimination (`c2_gaussian_elimination`) vs. Solvability/consistency criteria (`c2_kronecker_capelli`)
- Linear independence / dependence (`c3_linear_independence`) vs. Spanning sets and linear span (`c3_linear_combinations_span`) vs. Basis and dimension (`c3_basis_dimension_coordinates`)
- Algebraic form and conjugate of complex numbers (`c1_complex_numbers_algebraic`) vs. Polar/trigonometric form, De Moivre's theorem, and roots of unity (`c1_complex_numbers_trigonometric`)
- Algebraic structures: Group (`c1_groups`) vs. Ring (`c1_rings`) vs. Field (`c1_fields`)
- Subspaces and subspace criteria (`c3_subspaces`) vs. Orthogonal projection and orthogonal complement (`c5_orthogonal_projection`)

# Tag List

## Part I: Calculus 1 ("subject": "Calculus 1")

### Chapter 1: Differential Calculus of Single-Variable Functions
| Tag | Meaning |
|-----|---------|
| `c1_function_concepts` | Function concepts: domain, range, even/odd, periodic, composite, inverse |
| `c1_elementary_functions` | Elementary functions: power, exponential, logarithmic, trigonometric, inverse trig |
| `c1_sequences` | Sequences: monotonicity, boundedness, limits of sequences, squeeze theorem, Cauchy |
| `c1_function_limits` | Limits of single-variable functions: definition, one-sided limits, basic limit operations |
| `c1_infinitesimals_infinities` | Infinitesimals/infinities: order comparison, equivalent substitution, truncation |
| `c1_continuous_functions` | Continuous functions: continuity at a point/on an interval, IVT, discontinuity classification (type I/II), Heine-Cantor |
| `c1_derivatives_differentials` | Derivatives & differentials (1st and higher order): Leibniz formula, chain rule, inverse function derivative, linear approximation |
| `c1_taylor_maclaurin` | Mean value theorems (Fermat, Rolle, Lagrange, Cauchy) and Taylor/Maclaurin expansions (single-variable) |
| `c1_lhospital_rule` | L'Hôpital's rule, indeterminate power forms (1^∞, 0^0, ∞^0), comparing standard infinities |
| `c1_monotonic_functions` | Monotonic functions and derivative-based monotonicity tests |
| `c1_single_variable_extrema` | Extrema of single-variable functions |
| `c1_curve_sketching` | Curve sketching, asymptotes (vertical/horizontal/oblique), parametric curves, polar curves |

### Chapter 2: Integral Calculus of Single-Variable Functions
| Tag | Meaning |
|-----|---------|
| `c2_indefinite_integrals` | Indefinite integrals: antiderivatives, substitution, integration by parts, rational/trig/irrational integrals, Euler substitution |
| `c2_definite_integrals` | Definite integrals: Riemann sums, Newton-Leibniz, differentiation under integral sign, even/odd integrands |
| `c2_improper_infinite_intervals` | Improper integrals with infinite bounds |
| `c2_improper_unbounded_functions` | Improper integrals of unbounded functions (singular points) |
| `c2_improper_absolute_conditional` | Absolute vs. conditional convergence of improper integrals |
| `c2_improper_convergence_tests` | Convergence tests: comparison test (1st and 2nd) for improper integrals |
| `c2_app_plane_area` | Area computation: Cartesian, parametric, polar coordinates |
| `c2_app_arc_length` | Arc length: Cartesian, parametric, polar coordinates |
| `c2_app_solid_volume` | Volume: cross-sections, solids of revolution (around Ox, Oy) |
| `c2_app_surface_of_revolution` | Surface area of revolution |

### Chapter 3: Multivariable Functions (for disambiguation only)
| Tag | Meaning |
|-----|---------|
| `c3_multivariable_limits` | Limits and continuity of multivariable functions |
| `c3_partial_derivatives` | First-order partial derivatives |
| `c3_total_differentials` | Total differential and multivariable linear approximation |
| `c3_chain_rule` | Chain rule for multivariable functions, Jacobian |
| `c3_higher_order_derivatives` | Higher-order partials (Schwarz), higher-order differentials, multivariable Taylor/Maclaurin |
| `c3_implicit_functions` | Implicit functions and their derivatives, tangent lines |
| `c3_unconstrained_extrema` | Unconstrained extrema: critical points, Δ = B² − AC test |
| `c3_global_extrema` | Global max/min on closed bounded domains |

## Part II: Algebra ("subject": "Algebra")

### Chapter 1: Sets, Logic, Mappings, and Complex Numbers
| Tag | Meaning |
|-----|---------|
| `c1_logic` | Mathematical logic: propositions, logical connectives (AND, OR, NOT, implication, equivalence), truth tables, tautologies, laws of logic, universal ($\forall$) and existential ($\exists$) quantifiers, negation of quantified statements |
| `c1_set_theory` | Set theory: sets, subsets, set operations (union, intersection, set difference, complement, Cartesian product), set identities, De Morgan's laws for sets |
| `c1_mappings` | Mappings: definition, domain, codomain, range, image of a subset $f(A)$, inverse image / preimage $f^{-1}(B)$, composition of mappings $g \circ f$ |
| `c1_injective_surjective_bijective` | Classification of mappings: injective (one-to-one), surjective (onto), bijective mappings, invertible mappings and inverse mapping $f^{-1}$ |
| `c1_groups` | Group structure: binary operations, group axioms, abelian (commutative) groups, subgroups, identity and inverse elements, group isomorphism |
| `c1_rings` | Ring structure: ring axioms, commutative rings, rings with identity (unity), subrings, zero divisors, integral domains |
| `c1_fields` | Field structure: field axioms, subfields, characteristic of a field, standard number fields ($\mathbb{Q}, \mathbb{R}, \mathbb{C}, \mathbb{Z}_p$) |
| `c1_complex_numbers_algebraic` | Complex numbers in algebraic form: standard form $z = a + bi$, real and imaginary parts, complex conjugate $\bar{z}$, modulus $|z|$, basic arithmetic operations ($+, -, \times, /$, powers), solving polynomial equations in $\mathbb{C}$ |
| `c1_complex_numbers_trigonometric` | Complex numbers in trigonometric form: polar form $r(\cos \varphi + i\sin \varphi)$, argument, Euler's formula $e^{i\varphi}$, De Moivre's theorem, integer powers $z^n$, $n$-th roots of complex numbers, roots of unity |

### Chapter 2: Matrices, Determinants, and Systems of Linear Equations
| Tag | Meaning |
|-----|---------|
| `c2_matrix_operations` | Matrix operations: matrix addition, scalar multiplication, matrix multiplication, transpose, powers of matrices, trace, special matrix types (square, identity, zero, diagonal, symmetric, skew-symmetric), algebraic properties of matrix operations |
| `c2_determinants` | Determinants: definition, permutations, properties of determinants, row/column operations, Laplace cofactor expansion, evaluation methods (triangular reduction, recursion, Vandermonde), adjugate matrix, invertible matrices, matrix inverse via adjugate formula $A^{-1} = \frac{1}{\det A}\text{adj}(A)$ |
| `c2_matrix_rank` | Matrix rank: definition via subdeterminants/minors, computation of rank using elementary row operations (row echelon form), properties of rank, rank inequalities (Sylvester, Frobenius) |
| `c2_cramer_rule` | Cramer's rule: systems of linear equations with square coefficient matrix and non-zero determinant ($\det A \neq 0$), Cramer's formulas $x_i = \frac{\det A_i}{\det A}$ |
| `c2_kronecker_capelli` | Solvability and consistency of linear systems: general system $Ax = b$, augmented matrix $\bar{A} = [A \mid b]$, Kronecker-Capelli (Rouché-Capelli) theorem, conditions for existence of solutions, uniqueness, infinite solutions, degree of freedom |
| `c2_gaussian_elimination` | Gaussian elimination: solving general linear systems via elementary row operations, forward elimination, back substitution, free variables, pivot variables, parameterized general solution, fundamental system of solutions for homogeneous linear systems $Ax = 0$ |

### Chapter 3: Vector Spaces
| Tag | Meaning |
|-----|---------|
| `c3_vector_spaces` | Vector spaces: definition of vector space over a field $K$, 8 vector space axioms, verification of axioms, basic algebraic properties of vector spaces |
| `c3_subspaces` | Vector subspaces: definition, necessary and sufficient criteria for a subset $W \subseteq V$ to be a subspace (closed under addition and scalar multiplication), intersection and sum of subspaces, direct sums |
| `c3_linear_combinations_span` | Linear combinations and spanning sets: linear combination of vectors, linear span $\text{span}(S)$, subspace generated/spanned by a vector set, generating/spanning sets of a vector space |
| `c3_linear_independence` | Linear independence and dependence: definition of linearly independent and linearly dependent vector systems, properties, testing linear independence via definition, determinants, or matrix rank |
| `c3_basis_dimension_coordinates` | Bases, dimension, and coordinates: definition of a basis, finite-dimensional vector spaces, dimension $\dim V$, coordinates of a vector relative to an ordered basis, standard bases of $\mathbb{R}^n$, polynomial spaces $P_n[x]$, and matrix spaces $M_{m \times n}(K)$ |
| `c3_rank_of_vector_set` | Rank of a vector set and spanned subspace: definition of rank of a vector system, computing rank via elementary transformations, extracting a basis and determining dimension for the subspace $\text{span}(v_1, \dots, v_k)$ |
| `c3_change_of_basis` | Change of basis: transition matrix (change-of-basis matrix) $P$ between two bases, invertibility of transition matrix, coordinate transformation formulas $X = P X'$ and $X' = P^{-1} X$ |

### Chapter 4: Linear Mappings
| Tag | Meaning |
|-----|---------|
| `c4_linear_mappings` | Linear mappings: definition of linear mappings / transformations $f: V \to W$, linear operators $f: V \to V$, linearity condition $f(au + bv) = af(u) + bf(v)$, image of linear combinations, linear isomorphisms |
| `c4_kernel_and_image` | Kernel and image: definition of $\text{Ker}(f)$ and $\text{Im}(f)$, finding bases and dimensions of kernel and image, injectivity and surjectivity criteria via kernel and image ($\text{Ker}(f) = \{0\} \iff f$ is injective) |
| `c4_rank_nullity_theorem` | Rank-Nullity Theorem: rank of a linear mapping $\text{rank}(f) = \dim(\text{Im}(f))$, nullity $\dim(\text{Ker}(f))$, dimension theorem $\dim(\text{Ker}(f)) + \dim(\text{Im}(f)) = \dim V$ |
| `c4_matrix_representation` | Matrix representation of linear mappings: matrix of a linear mapping $f: V \to W$ relative to given pairs of bases, computing image coordinates via matrix multiplication $[f(x)] = A [x]$ |
| `c4_matrix_under_change_of_basis` | Matrix representation under change of basis: transformation of matrix representation under basis change ($A' = Q^{-1} A P$), similar matrices for linear operators ($A' = P^{-1} A P$), matrix similarity invariants (trace, determinant, rank) |
| `c4_eigenvalues_eigenvectors_matrix` | Eigenvalues and eigenvectors of a matrix: characteristic equation $\det(A - \lambda I) = 0$, characteristic polynomial, eigenvalues, eigenvectors, eigenspaces $E_\lambda = \text{Ker}(A - \lambda I)$ of square matrices |
| `c4_eigenvalues_eigenvectors_operator` | Eigenvalues and eigenvectors of a linear operator: definition $f(v) = \lambda v$ ($v \neq 0$), eigenspaces, invariant subspaces, coordinate-free formulation |
| `c4_matrix_diagonalization` | Matrix diagonalization: diagonalizable matrices, algebraic vs. geometric multiplicity condition, constructing invertible modal matrix $P$ and diagonal matrix $D$ such that $P^{-1} A P = D$ |
| `c4_minimal_polynomial` | Minimal polynomial: definition of minimal polynomial of a matrix or operator, properties, relation to characteristic polynomial, Cayley-Hamilton theorem ($p_A(A) = 0$), diagonalizability criteria via minimal polynomial |
| `c4_eigenvalue_properties` | Advanced properties of eigenvalues: algebraic and geometric multiplicities, spectral properties, trace as sum of eigenvalues $\text{tr}(A) = \sum \lambda_i$, determinant as product of eigenvalues $\det(A) = \prod \lambda_i$, eigenvalues of triangular and block matrices |
| `c4_diagonalization_applications` | Applications of matrix diagonalization: computing matrix powers $A^k$, matrix exponential $e^{At}$, solving systems of linear difference equations / recurrence relations, systems of linear differential equations |

### Chapter 5: Quadratic Forms and Euclidean Spaces
| Tag | Meaning |
|-----|---------|
| `c5_quadratic_forms` | Quadratic forms: definition of quadratic forms, polynomial expression, symmetric matrix representation of a quadratic form $Q(x) = x^T A x$, variable substitutions |
| `c5_quadratic_form_definiteness` | Definiteness and classification of quadratic forms: positive definite, negative definite, positive semidefinite, negative semidefinite, indefinite quadratic forms; Sylvester's criterion (leading principal minors test) |
| `c5_bilinear_forms` | Bilinear forms: definition, symmetric and skew-symmetric bilinear forms, matrix of a bilinear form, polar form of a quadratic form, relation between bilinear and quadratic forms |
| `c5_lagrange_reduction` | Lagrange's reduction method: reducing a quadratic form to canonical / diagonal form (sum of squares) by completing squares, non-singular coordinate transformations |
| `c5_jacobi_reduction` | Jacobi's reduction method: reducing a quadratic form to canonical form using leading principal minors $\Delta_k \neq 0$, canonical coefficients $\frac{\Delta_{k-1}}{\Delta_k}$ |
| `c5_canonical_form_inertia` | Canonical form and Sylvester's Law of Inertia: canonical form, normal form, positive and negative indices of inertia, signature, invariance of signature under real non-singular transformations |
| `c5_inner_product_spaces` | Inner product spaces (Euclidean spaces): axioms of inner product $\langle u, v \rangle$, induced norm/length $\|v\| = \sqrt{\langle u, v \rangle}$, metric/distance, Cauchy-Schwarz inequality, triangle inequality, angle between vectors, orthogonality |
| `c5_gram_schmidt_process` | Gram-Schmidt orthogonalization: orthogonal and orthonormal sets of vectors, constructing an orthonormal basis from an arbitrary basis, normalization of vectors |
| `c5_orthogonal_projection` | Orthogonal projection and orthogonal complement: orthogonal projection of a vector onto a subspace $P_W(v)$, orthogonal complement $W^\perp$, direct sum decomposition $V = W \oplus W^\perp$, shortest distance from a vector to a subspace |
| `c5_orthogonal_diagonalization` | Orthogonal diagonalization of symmetric matrices: real spectral theorem (real eigenvalues, orthogonal eigenvectors from distinct eigenspaces), orthogonal matrices $Q^{-1} = Q^T$, finding orthogonal matrix $Q$ such that $Q^T A Q = D$ |
| `c5_orthogonal_reduction_quadratic_form` | Orthogonal canonical reduction of quadratic forms: reduction of quadratic forms to canonical form via orthogonal transformations (principal axis theorem) |
| `c5_conic_sections` | Classification and identification of plane curves: reduction of general second-degree equations in $\mathbb{R}^2$ ($Ax^2 + 2Bxy + Cy^2 + 2Dx + 2Ey + F = 0$) using rotation and translation, identifying ellipses, hyperbolas, parabolas, and degenerate cases |
| `c5_quadric_surfaces` | Classification and identification of quadric surfaces: reduction of general second-degree equations in $\mathbb{R}^3$ to standard form, identifying ellipsoids, hyperboloids (one/two sheets), elliptic/hyperbolic paraboloids, quadric cylinders, and cones |
| `c5_constrained_extrema` | Constrained extrema via orthogonal transformations: finding conditional maximum and minimum of a quadratic form $x^T A x$ subject to $\|x\| = 1$, Rayleigh quotient, maximum and minimum eigenvalues |

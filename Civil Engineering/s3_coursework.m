clear all;

%Inputs: Number of elements
%for 40 elem question: 
%   num_elems = 40
num_elems = 4;
num_nodes = num_elems + 1;

dof_per_node = 3;
nodes_per_elem = 2;
dof_per_elem = dof_per_node * nodes_per_elem;

%These are the nodes and coordinates for the problem using 4 elements
%These are used to calculate values corresponding to the 40 element
%problem, which is done in the function "new_value_calculator"
elem_nodes = [1 2; 2 3; 3 4; 4 5];
node_coordinates = [0 0; 0 0.15; 0 0.3; 0.6 0.3; 0.6 0.15];

%forces for the original 4 elem problem
p = [0;0;0;150*10^3;0;0;0;0;0;0;0;0;0;0;0]; 

%Creating the new nodes, based on the "num_elems" input
new_elem_nodes = zeros(num_elems, 2);
for i = 1:num_elems
    new_elem_nodes(i, 1) = i;
    new_elem_nodes(i, 2) = i+1;
end

%Function to generate new external force values and new coordinates
[new_p, new_coords] = new_value_calculator(node_coordinates, num_nodes, num_elems, 4);

%Assigning the new values
elem_nodes = new_elem_nodes;
p = new_p;
node_coordinates = new_coords;

%Declaring area, E and I
area = 0.02 * ones(num_elems, 1);
E = 2000 * ones(num_elems, 1);
I = 6*10^(-4) * ones(num_elems, 1); 

%Setting alpha and delta_t to an array of zeros
alpha = zeros(num_elems, 1);
delta_t = zeros(num_elems, 1);

%This is the number of degrees of freedom in the specified system
sys_dofs = dof_per_node * num_nodes;


%Fully Fixed Boundary Conditions:
%dof_bc_locations = [1 ; 2; sys_dofs-2; sys_dofs-1]; %locations of dof boundary conditions, where U = 0

%Pinned RHS Support Boundary Conditions:
dof_bc_locations = [1 ; 2; sys_dofs-2; sys_dofs-1; sys_dofs];

%Creating x and y arrays, for conveniance
x = node_coordinates(:, 1);
y = node_coordinates(:, 2);

%Number of constraints in the system
num_constraints = length(dof_bc_locations);

%Initialising matrices:
l = zeros(1, num_elems); %Length Vector
C = zeros(1, num_elems); %cosine vector
S = zeros(1, num_elems); %sine vector
AEL = zeros(1, num_elems); %Mechanical Properties
temp_prop = zeros(1, num_elems); %Temperature Properties 
elem_dofs_vector = zeros(num_elems, nodes_per_elem); %Degrees of Freedom matrix
K = zeros(sys_dofs, sys_dofs); %Global stiffness
F = zeros(sys_dofs, 1); %Internal Forces Vector


% Element Loop:

for e = 1:num_elems
    elem_dofs_vector(e, 1) = (elem_nodes(e, 1)*3) - 2 ;   %U_3i-2
    elem_dofs_vector(e, 2) = (elem_nodes(e, 1)*3) -1 ;  %U_3i-1
    elem_dofs_vector(e, 3) = (elem_nodes(e, 1)*3)  ;  %U_3i
    
    elem_dofs_vector(e, 4) = (elem_nodes(e, 2)*3) -2  ;   %U_3j - 2
    elem_dofs_vector(e, 5) = (elem_nodes(e, 2)*3) -1  ;   %U_3j - 1
    elem_dofs_vector(e, 6) = (elem_nodes(e, 2)*3)    ;   %U_3j
    
    
    
    i = elem_nodes(e, 1); % i node number, used for indexing
    j = elem_nodes(e, 2); % j node number, used for indexing
    
    xi = x(i); %x value for node i
    xj = x(j); %x value for node j
    
    yi = y(i); %y value for node i
    yj = y(j); %y value for node j
    
    l(e) = (((xj-xi)^2+(yj-yi)^2)^(0.5)); %length of element
    C(e) = (xj-xi)/l(e); %cosine value for element
    S(e) = (yj-yi)/l(e); %sine value for element
    
    %Below values are for conveniance
    c = C(e); %cosine
    s = S(e); %sine
    c2 = c^2; %cosine squared
    s2 = s^2; %sine squared
    cs = c*s; %(cosine)*(sine)
    
    AEL(e) = area(e)*E(e)/l(e); % mechanical properties for element
    
    temp_prop(e) = area(e) * E(e) * alpha(e) * delta_t(e); %thermal properties for element
    
    %transformation matrix
    trans_matrix = [s c 0 0 0 0; -s c 0 0 0 0; 0 0 1 0 0 0; 0 0 0 c s 0; 0 0 0 -s c 0; 0 0 0 0 0 1 ];
    
    elem_length = l(e); %for conveniance
    elem_area = area(e); %for conveniance
    elem_i = I(e); %for conveniance
    
    %K bar e matrix
    k_bar_e = E(e)*elem_i/elem_length^3*[elem_area*elem_length^2/elem_i 0 0  -elem_area*elem_length^2/elem_i 0 0; 
                                        0 12 6*elem_length 0 -12 6*elem_length; 
                                        0 6*elem_length 4*elem_length^2 0 -6*elem_length 2*elem_length^2;
                                        -elem_area*elem_length^2/elem_i 0 0 elem_area*elem_length^2/elem_i 0 0;
                                        0 -12 -6*elem_length 0 12 -6*elem_length;
                                        0 6*elem_length 2*elem_length^2 0 -6*elem_length 4*elem_length^2];
    
    %calculating element stiffness matrix
    ke = transpose(trans_matrix)* k_bar_e * trans_matrix;
    
    %calculating internal forces matrix, due thermal properties
    fe = temp_prop(e) * trans_matrix;
    
    %selecting global degrees of freedom for this element from all the 
    %degrees of freedom. These will be used to assign
    %values to internal force matrix and global stifness matrix
    global_dofs = elem_dofs_vector(e, :);
    
    %element row loop:
    for i= 1:dof_per_elem
        %For each row, add the corresponding element internal forces value 
        %to the existing global internal forces vector
        F(global_dofs(i)) = F(global_dofs(i)) + fe(i);
        
        %element column loop:
        for j = 1:dof_per_elem
            %Iterating through column in row.
            %Adding element stiffness to existing global stiffness matrix
            K(global_dofs(i), global_dofs(j)) = K(global_dofs(i), global_dofs(j))+ ke(i, j);
            
        end
        
    end
    
    
    
end

%Apply Boundary Conditions

for c = 1:num_constraints
    i = dof_bc_locations(c); %selecting dof where boundary condition applies
    K(i, :) = 0; %appling boundary condition to corresponding row
    K(:, i) = 0; %applying boundary condition to corresponding column
    F(i) = 0; %applying boundary condition to internal forced vector
end

PF = p + F; %Summing internal and external forces to get total force
active_dofs=setdiff([1:sys_dofs],[dof_bc_locations]);  %produce a list of active DOFs
Kr = K(active_dofs,active_dofs);    %produce a reduced stiffness matrix
Fr = PF(active_dofs);             %produce a reduced force vector

U = Kr\Fr  %solving for displacement and printing in console


%post processing, to find internal element forces:

u_complete = zeros(sys_dofs, 1);%complete u values, including zero values
for j=1:size(active_dofs, 2)
   u_index = active_dofs(j);
   u_complete(u_index) = U(j);
end

%nodal forces
nodal_force = K*u_complete;

elem_forces = zeros(num_elems, dof_per_elem);



for e = 1:num_elems
    elem_dofs_vector(e, 1) = (elem_nodes(e, 1)*3) - 2 ;   %U_3i-2
    elem_dofs_vector(e, 2) = (elem_nodes(e, 1)*3) -1 ;  %U_3i-1
    elem_dofs_vector(e, 3) = (elem_nodes(e, 1)*3)  ;  %U_3i
    
    elem_dofs_vector(e, 4) = (elem_nodes(e, 2)*3) -2  ;   %U_3j - 2
    elem_dofs_vector(e, 5) = (elem_nodes(e, 2)*3) -1  ;   %U_3j - 1
    elem_dofs_vector(e, 6) = (elem_nodes(e, 2)*3)    ;   %U_3j
    
    
    
    i = elem_nodes(e, 1); % i node number, used for indexing
    j = elem_nodes(e, 2); % j node number, used for indexing
    
    xi = x(i); %x value for node i
    xj = x(j); %x value for node j
    
    yi = y(i); %y value for node i
    yj = y(j); %y value for node j
    
    l(e) = (((xj-xi)^2+(yj-yi)^2)^(0.5)); %length of element
    C(e) = (xj-xi)/l(e); %cosine value for element
    S(e) = (yj-yi)/l(e); %sine value for element
    
    %Below values are for conveniance
    c = C(e); %cosine
    s = S(e); %sine
    c2 = c^2; %cosine squared
    s2 = s^2; %sine squared
    cs = c*s; %(cosine)*(sine)
    
    AEL(e) = area(e)*E(e)/l(e); % mechanical properties for element
    
    temp_prop(e) = area(e) * E(e) * alpha(e) * delta_t(e); %thermal properties for element
    
    %transformation matrix
    trans_matrix = [s c 0 0 0 0; -s c 0 0 0 0; 0 0 1 0 0 0; 0 0 0 c s 0; 0 0 0 -s c 0; 0 0 0 0 0 1 ];
    
    elem_length = l(e); %for conveniance
    elem_area = area(e); %for conveniance
    elem_i = I(e); %for conveniance
    
    %K bar e matrix
    k_bar_e = E(e)*elem_i/elem_length^3*[elem_area*elem_length^2/elem_i 0 0  -elem_area*elem_length^2/elem_i 0 0; 
                                        0 12 6*elem_length 0 -12 6*elem_length; 
                                        0 6*elem_length 4*elem_length^2 0 -6*elem_length 2*elem_length^2;
                                        -elem_area*elem_length^2/elem_i 0 0 elem_area*elem_length^2/elem_i 0 0;
                                        0 -12 -6*elem_length 0 12 -6*elem_length;
                                        0 6*elem_length 2*elem_length^2 0 -6*elem_length 4*elem_length^2];
    
    %calculating element stiffness matrix
    ke = transpose(trans_matrix)* k_bar_e * trans_matrix;
    
    %calculating internal forces matrix, due thermal properties
    fe = temp_prop(e) * trans_matrix;
    
    %selecting global degrees of freedom for this element from all the 
    %degrees of freedom. 
    global_dofs = elem_dofs_vector(e, :);
    
    %Index/position of degrees of freedom. Used to select the relevant
    %subset from the matrix containing all the degrees of freedom
    dof_start_index = global_dofs(1);
    dof_end_index = global_dofs(end);
    
    %selecting degrees of freedom corresponding to this element
    u_elem = u_complete(dof_start_index:dof_end_index);
    
    %calculating internal forces for this element
    EF = k_bar_e*trans_matrix*u_elem
    
    %storing inernal forces for this elems in a matrix which will contain
    %the internal forces for all elements
    elem_forces(e,:) = EF;
     
end



function [new_p, new_coords] = new_value_calculator(original_nodal_coords, num_nodes, new_num_elems, original_num_elems)
    onc = original_nodal_coords; %for conveniance
    new_coords = zeros(num_nodes, 2);
    new_p = zeros(3*num_nodes, 1);
    num_increments = new_num_elems/original_num_elems;
    
    %loop for each coordinate
    for onc_row = 1:length(onc) -1
        current_x = onc(onc_row, 1);
        current_y = onc(onc_row, 2);
        next_x = onc(onc_row + 1, 1);
        next_y = onc(onc_row + 1, 2);
        
        x_increment = (next_x - current_x)/num_increments;
        y_increment = (next_y - current_y)/num_increments;
        
        %loop to split each coordinate up into 10 new coordinates
        for n = 1:num_increments 
            index = onc_row * num_increments + n - num_increments +1;
            x_val = x_increment * n + current_x;
            y_val = y_increment * n + current_y;
            new_coords(index, 1) = x_val;
            new_coords(index, 2) = y_val;
         
        
        
        
            if x_val == 0 & y_val ==0.15
                p1 = 150*10^3;
            else
                p1 = 0;
            end

            p2 = 0;
            p3 = 0;

            new_p(index*3-2) = p1; %assigning x-force dof
            new_p(index*3 - 1) = p2; %assigning y-force dof
            new_p(index*3) = p3 ;%assigning moment dof
        
        end
        
    end
end













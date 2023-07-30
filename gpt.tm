% HEADERS
q0 q3 # 1

% TRANSITIONS
q0,0,q1,1 R
q0,0,q2,1 R
q0,1,q2,0 L
q1,0,q2,1 R
q1,1,q0,0 L
q1,1,q2,0 L
q2,0,q2,0 R
q2,1,q0,1 L
q2,1,q1,1 L
q2,#,q3,# S
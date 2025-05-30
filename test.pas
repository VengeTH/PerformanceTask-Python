PROGRAM P12;
VAR
   a : INTEGER;

PROCEDURE Proc1;
VAR
   a : REAL;
   k : INTEGER;

   PROCEDURE NestedProc1;
   VAR
      a, z : INTEGER;
   BEGIN {NestedProc1;}
      z := 888;
   END;  {NestedProc1;}

BEGIN {Proc1}

END;  {Proc1}

BEGIN {P12}
   a := 10;
END.  {P12}
from ortools.sat.python import cp_model
from typing import List, Dict, Tuple
from ..schemas.timetable import OptimizationRequest, OptimizationResponse, TimetableEntry, TimeSlot
import random

class TimetableOptimizer:
    def __init__(self):
        self.model = None
        self.solver = None
    
    def optimize(self, request: OptimizationRequest) -> OptimizationResponse:
        """
        Main optimization function using OR-Tools CP-SAT solver
        """
        try:
            self.model = cp_model.CpModel()
            
            # Create variables
            variables = self._create_variables(request)
            
            # Add constraints
            self._add_constraints(request, variables)
            
            # Set objective
            self._set_objective(variables)
            
            # Solve
            self.solver = cp_model.CpSolver()
            status = self.solver.Solve(self.model)
            
            if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
                timetable = self._extract_solution(request, variables)
                return OptimizationResponse(
                    success=True,
                    timetable=timetable,
                    optimization_score=self.solver.ObjectiveValue(),
                    message="Optimization completed successfully"
                )
            else:
                return OptimizationResponse(
                    success=False,
                    timetable=[],
                    optimization_score=0.0,
                    message="No feasible solution found"
                )
                
        except Exception as e:
            return OptimizationResponse(
                success=False,
                timetable=[],
                optimization_score=0.0,
                message=f"Optimization failed: {str(e)}"
            )
    
    def _create_variables(self, request: OptimizationRequest) -> Dict:
        """Create decision variables for the optimization problem"""
        variables = {}
        
        # Create binary variables for each course-faculty-classroom-timeslot combination
        for course in request.courses:
            for faculty in request.faculty:
                for classroom in request.classrooms:
                    for i, time_slot in enumerate(request.time_slots):
                        var_name = f"assign_{course.id}_{faculty.id}_{classroom.id}_{i}"
                        variables[var_name] = self.model.NewBoolVar(var_name)
        
        return variables
    
    def _add_constraints(self, request: OptimizationRequest, variables: Dict):
        """Add constraints to the optimization model"""
        
        # Each course must be assigned exactly once
        for course in request.courses:
            course_vars = []
            for faculty in request.faculty:
                for classroom in request.classrooms:
                    for i, time_slot in enumerate(request.time_slots):
                        var_name = f"assign_{course.id}_{faculty.id}_{classroom.id}_{i}"
                        course_vars.append(variables[var_name])
            self.model.Add(sum(course_vars) == 1)
        
        # No classroom conflicts
        for classroom in request.classrooms:
            for i, time_slot in enumerate(request.time_slots):
                classroom_vars = []
                for course in request.courses:
                    for faculty in request.faculty:
                        var_name = f"assign_{course.id}_{faculty.id}_{classroom.id}_{i}"
                        classroom_vars.append(variables[var_name])
                self.model.Add(sum(classroom_vars) <= 1)
        
        # No faculty conflicts
        for faculty in request.faculty:
            for i, time_slot in enumerate(request.time_slots):
                faculty_vars = []
                for course in request.courses:
                    for classroom in request.classrooms:
                        var_name = f"assign_{course.id}_{faculty.id}_{classroom.id}_{i}"
                        faculty_vars.append(variables[var_name])
                self.model.Add(sum(faculty_vars) <= 1)
    
    def _set_objective(self, variables: Dict):
        """Set optimization objective (maximize utilization)"""
        objective_vars = list(variables.values())
        self.model.Maximize(sum(objective_vars))
    
    def _extract_solution(self, request: OptimizationRequest, variables: Dict) -> List[TimetableEntry]:
        """Extract the solution from the solved model"""
        timetable = []
        
        for course in request.courses:
            for faculty in request.faculty:
                for classroom in request.classrooms:
                    for i, time_slot in enumerate(request.time_slots):
                        var_name = f"assign_{course.id}_{faculty.id}_{classroom.id}_{i}"
                        if self.solver.Value(variables[var_name]) == 1:
                            entry = TimetableEntry(
                                course_id=course.id,
                                faculty_id=faculty.id,
                                classroom_id=classroom.id,
                                time_slot=time_slot,
                                day=time_slot.day
                            )
                            timetable.append(entry)
        
        return timetable
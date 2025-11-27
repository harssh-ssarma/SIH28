"""
Resource Utilization Analytics Service
"""
from typing import List, Dict
from collections import defaultdict


class AnalyticsService:
    """Calculate resource utilization metrics"""
    
    @staticmethod
    def calculate_room_utilization(timetable_entries: List[Dict]) -> Dict:
        """Calculate room utilization heatmap data"""
        
        # Group by room
        by_room = defaultdict(list)
        for entry in timetable_entries:
            room = entry.get('room_number')
            if room:
                by_room[room].append(entry)
        
        # Calculate utilization per room
        total_slots = 30  # 5 days × 6 periods
        room_data = []
        
        for room, entries in by_room.items():
            utilization = (len(entries) / total_slots) * 100
            room_data.append({
                'room': room,
                'total_classes': len(entries),
                'utilization_percentage': round(utilization, 1),
                'status': 'high' if utilization > 70 else 'medium' if utilization > 40 else 'low'
            })
        
        # Sort by utilization
        room_data.sort(key=lambda x: x['utilization_percentage'], reverse=True)
        
        return {
            'rooms': room_data,
            'total_rooms': len(room_data),
            'avg_utilization': round(sum(r['utilization_percentage'] for r in room_data) / len(room_data), 1) if room_data else 0
        }
    
    @staticmethod
    def calculate_faculty_load(timetable_entries: List[Dict]) -> Dict:
        """Calculate faculty teaching load"""
        
        # Group by faculty
        by_faculty = defaultdict(list)
        for entry in timetable_entries:
            faculty = entry.get('faculty_name')
            if faculty:
                by_faculty[faculty].append(entry)
        
        # Calculate load per faculty
        faculty_data = []
        
        for faculty, entries in by_faculty.items():
            # Get unique courses
            courses = list(set(e.get('subject_code') for e in entries if e.get('subject_code')))
            
            faculty_data.append({
                'faculty': faculty,
                'total_classes': len(entries),
                'unique_courses': len(courses),
                'courses': courses,
                'load_status': 'overloaded' if len(entries) > 20 else 'optimal' if len(entries) > 10 else 'underutilized'
            })
        
        # Sort by load
        faculty_data.sort(key=lambda x: x['total_classes'], reverse=True)
        
        return {
            'faculty': faculty_data,
            'total_faculty': len(faculty_data),
            'avg_load': round(sum(f['total_classes'] for f in faculty_data) / len(faculty_data), 1) if faculty_data else 0
        }
    
    @staticmethod
    def calculate_department_matrix(timetable_entries: List[Dict]) -> Dict:
        """Calculate department interaction matrix"""
        
        # Get all departments
        departments = list(set(e.get('department_id', '') for e in timetable_entries if e.get('department_id')))
        
        # Build interaction matrix
        matrix = defaultdict(lambda: defaultdict(int))
        
        for entry in timetable_entries:
            dept = entry.get('department_id', '')
            batch = entry.get('batch_name', '')
            
            if dept and batch:
                # If batch != dept, it's cross-enrollment
                if batch != dept:
                    matrix[batch][dept] += 1
        
        # Convert to list format
        interactions = []
        for source in departments:
            for target in departments:
                if source != target and matrix[source][target] > 0:
                    interactions.append({
                        'source': source,
                        'target': target,
                        'count': matrix[source][target]
                    })
        
        return {
            'departments': departments,
            'interactions': interactions,
            'total_interactions': sum(i['count'] for i in interactions)
        }
    
    @staticmethod
    def get_utilization_summary(timetable_entries: List[Dict]) -> Dict:
        """Get overall utilization summary"""
        
        room_util = AnalyticsService.calculate_room_utilization(timetable_entries)
        faculty_load = AnalyticsService.calculate_faculty_load(timetable_entries)
        
        return {
            'total_entries': len(timetable_entries),
            'room_utilization': room_util['avg_utilization'],
            'faculty_avg_load': faculty_load['avg_load'],
            'total_rooms': room_util['total_rooms'],
            'total_faculty': faculty_load['total_faculty']
        }

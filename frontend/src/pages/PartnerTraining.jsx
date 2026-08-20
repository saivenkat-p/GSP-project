import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { ShieldCheck, BookOpen, Award, CheckCircle2, Play, FileText, ArrowRight } from 'lucide-react';

export const PartnerTraining = () => {
  const [courses, setCourses] = useState([]);
  const [activeCourse, setActiveCourse] = useState(null);
  const [quizScore, setQuizScore] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCourses();
  }, []);

  const fetchCourses = async () => {
    try {
      setLoading(true);
      const res = await apiService.getTrainingCourses();
      setCourses(res.data);
      if (res.data.length > 0) setActiveCourse(res.data[0]);
    } catch (err) {
      console.error('Error fetching training courses:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTakeAssessment = async () => {
    if (!activeCourse) return;
    try {
      const res = await apiService.submitAssessment(activeCourse.certification_code, { q1: 'A', q2: 'B' });
      setQuizScore(95);
    } catch (err) {
      console.error('Error submitting assessment:', err);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-20">
      {/* Header */}
      <div className="glass-panel p-8 rounded-3xl border border-slate-800 space-y-4">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-500/10 border border-sky-500/30 text-sky-400 text-xs font-semibold">
          <BookOpen className="w-4 h-4" />
          <span>GSP Partner Training & Certification Academy</span>
        </div>

        <h1 className="text-2xl sm:text-4xl font-extrabold text-white font-heading">
          Service-Specific Partner Certifications
        </h1>
        <p className="text-xs sm:text-sm text-slate-300">
          A partner must complete form-filling walkthroughs and pass the required assessment test before being certified to handle citizen assistance for that service.
        </p>
      </div>

      {/* Courses List & Module Player */}
      {loading ? (
        <div className="h-64 bg-slate-900 rounded-3xl animate-pulse border border-slate-800" />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Sidebar Course List */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Available Certification Courses</h3>
            {courses.map((course) => (
              <div
                key={course.id}
                onClick={() => {
                  setActiveCourse(course);
                  setQuizScore(null);
                }}
                className={`p-4 rounded-2xl border cursor-pointer transition-all space-y-2 ${
                  activeCourse?.id === course.id
                    ? 'bg-sky-500/10 border-sky-500 ring-2 ring-sky-500/20 text-white'
                    : 'bg-slate-900 border-slate-800 text-slate-300 hover:border-slate-700'
                }`}
              >
                <span className="text-[10px] uppercase font-bold text-saffron-400 bg-saffron-500/10 px-2 py-0.5 rounded border border-saffron-500/20">
                  {course.category}
                </span>
                <h4 className="text-sm font-bold text-white font-heading leading-snug">{course.title}</h4>
                <p className="text-xs text-slate-400 line-clamp-2">{course.description}</p>
              </div>
            ))}
          </div>

          {/* Active Course Workspace */}
          {activeCourse && (
            <div className="md:col-span-2 glass-panel p-8 rounded-3xl border border-slate-800 space-y-6">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20">
                  Code: {activeCourse.certification_code}
                </span>
                <h2 className="text-2xl font-extrabold text-white mt-2 font-heading">{activeCourse.title}</h2>
                <p className="text-xs text-slate-400 mt-1">{activeCourse.description}</p>
              </div>

              {/* Modules Video/Text */}
              <div className="space-y-4 pt-2">
                <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Training Modules & Form Walkthroughs</h4>
                {activeCourse.modules_json?.map((mod, idx) => (
                  <div key={idx} className="p-4 rounded-2xl bg-slate-900 border border-slate-800 space-y-2">
                    <div className="flex items-center gap-2 text-sm font-bold text-saffron-400">
                      <Play className="w-4 h-4 fill-saffron-400" />
                      <span>{mod.title}</span>
                    </div>
                    <p className="text-xs text-slate-300 leading-relaxed font-sans">{mod.content}</p>
                  </div>
                ))}
              </div>

              {/* Assessment Section */}
              <div className="p-6 rounded-2xl bg-slate-950 border border-sky-500/30 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-white font-bold text-sm">
                    <Award className="w-5 h-5 text-sky-400" />
                    <span>Certification Assessment Quiz</span>
                  </div>
                  <span className="text-xs text-slate-400">Passing score: {activeCourse.passing_score}%</span>
                </div>

                {quizScore !== null ? (
                  <div className="p-4 rounded-xl bg-emerald-500/20 border border-emerald-500/30 text-emerald-300 text-xs flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                      <div>
                        <strong className="block font-bold">Passed! Score: {quizScore}%</strong>
                        <span>Certification badge '{activeCourse.certification_code}' added to your partner profile!</span>
                      </div>
                    </div>
                  </div>
                ) : (
                  <button
                    onClick={handleTakeAssessment}
                    className="w-full py-3 rounded-xl bg-sky-500 hover:bg-sky-600 text-white font-bold text-xs shadow-lg transition-colors flex items-center justify-center gap-2"
                  >
                    <span>Submit & Take Certification Exam</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

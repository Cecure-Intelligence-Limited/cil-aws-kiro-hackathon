import React from 'react';
import { AssistantState } from '../types';

interface StepBadgeProps {
  step: AssistantState;
  currentState: AssistantState;
  isVisible?: boolean;
}

const stepLabels: Record<AssistantState, string> = {
  idle: 'Ready',
  capture: 'Capture',
  parseIntent: 'Parse',
  route: 'Route',
  execute: 'Execute',
  verify: 'Verify',
  respond: 'Respond',
  recover: 'Recover',
};

const stepColors: Record<AssistantState, { active: string; completed: string; pending: string }> = {
  idle: { active: 'bg-gray-500', completed: 'bg-gray-400', pending: 'bg-gray-200' },
  capture: { active: 'bg-blue-500', completed: 'bg-blue-400', pending: 'bg-gray-200' },
  parseIntent: { active: 'bg-purple-500', completed: 'bg-purple-400', pending: 'bg-gray-200' },
  route: { active: 'bg-indigo-500', completed: 'bg-indigo-400', pending: 'bg-gray-200' },
  execute: { active: 'bg-orange-500', completed: 'bg-orange-400', pending: 'bg-gray-200' },
  verify: { active: 'bg-yellow-500', completed: 'bg-yellow-400', pending: 'bg-gray-200' },
  respond: { active: 'bg-green-500', completed: 'bg-green-400', pending: 'bg-gray-200' },
  recover: { active: 'bg-red-500', completed: 'bg-red-400', pending: 'bg-gray-200' },
};

export const StepBadge: React.FC<StepBadgeProps> = ({ step, currentState, isVisible = true }) => {
  if (!isVisible) return null;

  const isActive = currentState === step;
  const isCompleted = getStepOrder(currentState) > getStepOrder(step) && currentState !== 'idle';
  const isPending = getStepOrder(currentState) < getStepOrder(step);

  const colors = stepColors[step];
  const bgColor = isActive ? colors.active : isCompleted ? colors.completed : colors.pending;
  const textColor = isActive || isCompleted ? 'text-white' : 'text-gray-600';

  return (
    <div className={`
      px-3 py-1 rounded-full text-xs font-medium transition-all duration-300 transform
      ${bgColor} ${textColor}
      ${isActive ? 'shadow-lg scale-105 animate-pulse' : ''}
      ${isCompleted ? 'shadow-md' : ''}
      ${isPending ? 'opacity-60' : 'opacity-100'}
    `}>
      <span className="flex items-center gap-1">
        {isCompleted && <span className="text-xs">✓</span>}
        {isActive && <span className="text-xs animate-spin">⟳</span>}
        {stepLabels[step]}
      </span>
    </div>
  );
};

function getStepOrder(state: AssistantState): number {
  const order = { 
    idle: 0, 
    capture: 1, 
    parseIntent: 2, 
    route: 3, 
    execute: 4, 
    verify: 5, 
    respond: 6, 
    recover: 7 
  };
  return order[state] ?? 0;
}

// Component for displaying all step badges
export const StepBadges: React.FC<{ currentState: AssistantState; showStepBadges: boolean }> = ({ 
  currentState, 
  showStepBadges 
}) => {
  const visibleSteps: AssistantState[] = ['capture', 'parseIntent', 'route', 'execute', 'verify', 'respond'];
  
  if (!showStepBadges) return null;

  return (
    <div className="flex justify-center space-x-2 mb-6 flex-wrap gap-2">
      {visibleSteps.map((step) => (
        <StepBadge 
          key={step} 
          step={step} 
          currentState={currentState}
          isVisible={showStepBadges}
        />
      ))}
      {currentState === 'recover' && (
        <StepBadge 
          step="recover" 
          currentState={currentState}
          isVisible={true}
        />
      )}
    </div>
  );
};
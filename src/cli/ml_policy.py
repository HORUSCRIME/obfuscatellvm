#!/usr/bin/env python3
"""ML-based policy generator for automatic obfuscation pass selection."""

import json
import random
import numpy as np
from typing import Dict, List, Tuple, Any
from pathlib import Path


class ObfuscationEnvironment:
    """Simplified environment for obfuscation policy learning."""
    
    def __init__(self):
        self.passes = [
            "string-encrypt", "junk-insert", "symbol-rename", 
            "cfg-flatten", "opaque-predicates", "virtualize", "decompiler-adversarial"
        ]
        self.state_size = 10  # Program features
        self.action_size = len(self.passes)
        self.reset()
    
    def reset(self) -> np.ndarray:
        """Reset environment and return initial state."""
        # Mock program features: size, complexity, function count, etc.
        self.state = np.random.rand(self.state_size)
        self.applied_passes = set()
        return self.state.copy()
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool]:
        """Apply pass and return new state, reward, done."""
        pass_name = self.passes[action]
        
        # Calculate reward based on security vs performance trade-off
        reward = 0.0
        
        if pass_name not in self.applied_passes:
            self.applied_passes.add(pass_name)
            
            # Security benefit (positive reward)
            security_weights = {
                "string-encrypt": 0.3,
                "junk-insert": 0.2,
                "symbol-rename": 0.1,
                "cfg-flatten": 0.4,
                "opaque-predicates": 0.3,
                "virtualize": 0.5,
                "decompiler-adversarial": 0.6
            }
            reward += security_weights.get(pass_name, 0.1)
            
            # Performance penalty (negative reward)
            performance_penalties = {
                "string-encrypt": -0.1,
                "junk-insert": -0.05,
                "symbol-rename": -0.02,
                "cfg-flatten": -0.3,
                "opaque-predicates": -0.15,
                "virtualize": -0.4,
                "decompiler-adversarial": -0.2
            }
            reward += performance_penalties.get(pass_name, -0.05)
            
            # Update state (simplified)
            self.state[action % self.state_size] += 0.1
        else:
            # Penalty for redundant application
            reward = -0.1
        
        # Episode ends after applying 5 passes or all passes
        done = len(self.applied_passes) >= 5 or len(self.applied_passes) >= len(self.passes)
        
        return self.state.copy(), reward, done


class SimpleQLearningAgent:
    """Simple Q-learning agent for pass selection."""
    
    def __init__(self, state_size: int, action_size: int, learning_rate: float = 0.1):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.epsilon = 0.1  # Exploration rate
        self.gamma = 0.95   # Discount factor
        
        # Simple Q-table approximation (in practice, would use neural network)
        self.q_table = np.random.rand(100, action_size) * 0.01  # Discretized states
    
    def get_state_index(self, state: np.ndarray) -> int:
        """Convert continuous state to discrete index."""
        # Simple hash-based discretization
        state_hash = hash(tuple(np.round(state, 2))) % 100
        return abs(state_hash)
    
    def choose_action(self, state: np.ndarray) -> int:
        """Choose action using epsilon-greedy policy."""
        if random.random() < self.epsilon:
            return random.randint(0, self.action_size - 1)
        
        state_idx = self.get_state_index(state)
        return np.argmax(self.q_table[state_idx])
    
    def update(self, state: np.ndarray, action: int, reward: float, next_state: np.ndarray):
        """Update Q-values."""
        state_idx = self.get_state_index(state)
        next_state_idx = self.get_state_index(next_state)
        
        current_q = self.q_table[state_idx, action]
        max_next_q = np.max(self.q_table[next_state_idx])
        
        new_q = current_q + self.learning_rate * (reward + self.gamma * max_next_q - current_q)
        self.q_table[state_idx, action] = new_q


class MLPolicyGenerator:
    """ML-based policy generator for obfuscation."""
    
    def __init__(self):
        self.env = ObfuscationEnvironment()
        self.agent = SimpleQLearningAgent(self.env.state_size, self.env.action_size)
        self.training_episodes = 1000
    
    def train(self) -> Dict[str, Any]:
        """Train the ML agent."""
        episode_rewards = []
        
        for episode in range(self.training_episodes):
            state = self.env.reset()
            total_reward = 0
            
            while True:
                action = self.agent.choose_action(state)
                next_state, reward, done = self.env.step(action)
                
                self.agent.update(state, action, reward, next_state)
                
                state = next_state
                total_reward += reward
                
                if done:
                    break
            
            episode_rewards.append(total_reward)
            
            # Decay exploration
            if episode % 100 == 0:
                self.agent.epsilon = max(0.01, self.agent.epsilon * 0.95)
        
        return {
            "episodes": self.training_episodes,
            "final_reward": episode_rewards[-1],
            "average_reward": np.mean(episode_rewards[-100:]),
            "convergence": len(episode_rewards)
        }
    
    def generate_policy(self, program_features: Dict[str, float]) -> List[str]:
        """Generate obfuscation policy for given program."""
        # Convert program features to state vector
        state = np.array([
            program_features.get("size", 0.5),
            program_features.get("complexity", 0.5),
            program_features.get("function_count", 0.5),
            program_features.get("loop_count", 0.5),
            program_features.get("branch_count", 0.5),
            program_features.get("performance_critical", 0.0),
            program_features.get("security_level", 0.5),
            program_features.get("target_platform", 0.5),
            program_features.get("code_size_limit", 0.5),
            program_features.get("runtime_limit", 0.5)
        ])
        
        # Generate pass sequence
        selected_passes = []
        current_state = state.copy()
        
        for _ in range(5):  # Max 5 passes
            action = self.agent.choose_action(current_state)
            pass_name = self.env.passes[action]
            
            if pass_name not in selected_passes:
                selected_passes.append(pass_name)
                # Update state (simplified)
                current_state[action % len(current_state)] += 0.1
        
        return selected_passes
    
    def evaluate_policy(self, policy: List[str], program_features: Dict[str, float]) -> Dict[str, float]:
        """Evaluate policy effectiveness."""
        # Mock evaluation metrics
        security_score = 0.0
        performance_score = 1.0
        
        security_weights = {
            "string-encrypt": 0.15,
            "junk-insert": 0.10,
            "symbol-rename": 0.05,
            "cfg-flatten": 0.25,
            "opaque-predicates": 0.20,
            "virtualize": 0.30,
            "decompiler-adversarial": 0.35
        }
        
        performance_penalties = {
            "string-encrypt": 0.05,
            "junk-insert": 0.03,
            "symbol-rename": 0.01,
            "cfg-flatten": 0.20,
            "opaque-predicates": 0.10,
            "virtualize": 0.25,
            "decompiler-adversarial": 0.15
        }
        
        for pass_name in policy:
            security_score += security_weights.get(pass_name, 0.05)
            performance_score -= performance_penalties.get(pass_name, 0.02)
        
        # Normalize scores
        security_score = min(1.0, security_score)
        performance_score = max(0.0, performance_score)
        
        # Combined score (weighted)
        combined_score = 0.6 * security_score + 0.4 * performance_score
        
        return {
            "security_score": security_score,
            "performance_score": performance_score,
            "combined_score": combined_score,
            "pass_count": len(policy)
        }


def analyze_program_features(source_path: str) -> Dict[str, float]:
    """Extract features from source code for ML policy generation."""
    try:
        with open(source_path) as f:
            content = f.read()
        
        # Simple feature extraction
        lines = content.split('\n')
        features = {
            "size": min(1.0, len(content) / 10000),  # Normalized size
            "complexity": min(1.0, content.count('{') / 50),  # Rough complexity
            "function_count": min(1.0, content.count('(') / 20),  # Function calls
            "loop_count": min(1.0, (content.count('for') + content.count('while')) / 10),
            "branch_count": min(1.0, (content.count('if') + content.count('switch')) / 20),
            "performance_critical": 0.5,  # Default assumption
            "security_level": 0.7,  # Default high security need
            "target_platform": 0.5,  # Cross-platform
            "code_size_limit": 0.8,  # Moderate size constraints
            "runtime_limit": 0.6   # Moderate performance requirements
        }
        
        return features
        
    except Exception:
        # Return default features if analysis fails
        return {
            "size": 0.5, "complexity": 0.5, "function_count": 0.5,
            "loop_count": 0.5, "branch_count": 0.5, "performance_critical": 0.5,
            "security_level": 0.5, "target_platform": 0.5,
            "code_size_limit": 0.5, "runtime_limit": 0.5
        }


if __name__ == "__main__":
    # Demo ML policy generation
    print("Training ML policy generator...")
    
    generator = MLPolicyGenerator()
    training_results = generator.train()
    
    print(f"Training completed:")
    print(f"  Episodes: {training_results['episodes']}")
    print(f"  Final reward: {training_results['final_reward']:.3f}")
    print(f"  Average reward: {training_results['average_reward']:.3f}")
    
    # Generate policy for sample program
    features = analyze_program_features("examples/math.c")
    policy = generator.generate_policy(features)
    evaluation = generator.evaluate_policy(policy, features)
    
    print(f"\nGenerated policy for math.c:")
    print(f"  Passes: {policy}")
    print(f"  Security score: {evaluation['security_score']:.3f}")
    print(f"  Performance score: {evaluation['performance_score']:.3f}")
    print(f"  Combined score: {evaluation['combined_score']:.3f}")
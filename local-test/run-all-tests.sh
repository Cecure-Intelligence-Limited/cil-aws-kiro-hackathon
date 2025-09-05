#!/bin/bash
echo "========================================"
echo "Aura Desktop Assistant - Test Suite"
echo "========================================"
echo ""

PASSED=0
TOTAL=0

# Test 1: Backend API Tests
echo "🧪 Running Backend API Tests..."
((TOTAL++))
cd backend
source venv/bin/activate
python -m pytest tests/ -v --tb=short
if [ $? -eq 0 ]; then
    echo "✅ Backend tests passed"
    ((PASSED++))
else
    echo "❌ Backend tests failed"
fi
cd ..

# Test 2: Frontend Component Tests
echo "🧪 Running Frontend Component Tests..."
((TOTAL++))
npm test -- --run --reporter=verbose
if [ $? -eq 0 ]; then
    echo "✅ Frontend tests passed"
    ((PASSED++))
else
    echo "❌ Frontend tests failed"
fi

# Test 3: Integration Tests
echo "🧪 Running Integration Tests..."
((TOTAL++))
python3 local-test/test-integration.py
if [ $? -eq 0 ]; then
    echo "✅ Integration tests passed"
    ((PASSED++))
else
    echo "❌ Integration tests failed"
fi

# Test 4: Performance Tests
echo "🧪 Running Performance Tests..."
((TOTAL++))
python3 local-test/test-performance.py
if [ $? -eq 0 ]; then
    echo "✅ Performance tests passed"
    ((PASSED++))
else
    echo "❌ Performance tests failed"
fi

# Test 5: Security Tests
echo "🧪 Running Security Tests..."
((TOTAL++))
python3 local-test/test-security.py
if [ $? -eq 0 ]; then
    echo "✅ Security tests passed"
    ((PASSED++))
else
    echo "❌ Security tests failed"
fi

# Summary
echo ""
echo "========================================"
echo "Test Results Summary"
echo "========================================"
echo "Tests Passed: $PASSED/$TOTAL"
echo ""

if [ $PASSED -eq $TOTAL ]; then
    echo "🎉 All tests passed! Aura is ready for demo."
    exit 0
else
    echo "⚠️  Some tests failed. Check output above for details."
    exit 1
fi
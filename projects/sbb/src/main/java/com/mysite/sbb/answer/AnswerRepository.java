package com.mysite.sbb.answer;

import org.springframework.data.jpa.repository.JpaRepository;

import com.mysite.sbb.question.Question;

public interface AnswerRepository extends JpaRepository<Answer, Integer>{
}

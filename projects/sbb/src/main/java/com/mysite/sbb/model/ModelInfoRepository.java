package com.mysite.sbb.model;

import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;

public interface ModelInfoRepository extends JpaRepository<ModelInfo, Integer> {

    Optional<ModelInfo> findTopByOrderByIdDesc();

}
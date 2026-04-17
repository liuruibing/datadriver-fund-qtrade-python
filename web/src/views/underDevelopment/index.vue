<!--
 * @Description: 
 * @Author: 
 * @Date: 2025-12-01 10:19:55
 * @LastEditors: 
 * @LastEditTime: 2025-12-01 10:23:23
-->
<template>
	<fs-page>
		<div class="under-development-container">
			<el-card class="development-card" shadow="never">
				<div class="development-content">
					<div class="development-icon">
						<i class="el-icon-Setting"></i>
					</div>
					<h2 class="development-title">功能开发中</h2>
				</div>
			</el-card>
		</div>
	</fs-page>
</template>

<script setup lang="ts">
import { ref } from 'vue';
</script>

<style scoped lang="scss">
.under-development-container {
	display: flex;
	justify-content: center;
	align-items: center;
	min-height: 60vh;
	padding: 20px;
}

.development-card {
	max-width: 500px;
	width: 100%;
	text-align: center;
}

.development-content {
	padding: 40px 20px;
}

.development-icon {
	font-size: 80px;
	color: #409eff;
	margin-bottom: 24px;

	.el-icon-Setting {
		display: block;
		animation: rotate 3s linear infinite;
	}
}

@keyframes rotate {
	from {
		transform: rotate(0deg);
	}
	to {
		transform: rotate(360deg);
	}
}

.development-title {
	font-size: 28px;
	color: #303133;
	margin-bottom: 16px;
	font-weight: 500;
}
</style>
